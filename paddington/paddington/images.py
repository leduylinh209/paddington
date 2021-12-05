import hashlib
import os.path
from collections import OrderedDict
from contextlib import contextmanager
from io import BytesIO

from django.core import checks
from django.core.files import File
from django.db import models
from django.forms.utils import flatatt
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from willow.image import Image as WillowImage

from paddington import image_operations


class SourceImageIOError(IOError):
    pass


class InvalidFilterSpecError(ValueError):
    pass


def get_rendition_upload_to(instance, filename):
    """
    Obtain a valid upload path for an image rendition file.
    This needs to be a module-level function so that it can be referenced within migrations,
    but simply delegates to the `get_upload_to` method of the instance, so that AbstractRendition
    subclasses can override it.
    """
    return instance.get_upload_to(filename)


class AbtractImage(models.Model):
    """
    Abtract model for models with main image field name is 'image'
    """

    @cached_property
    def image_thumbnail(self):
        if not self.image:
            return None
        return self.get_rendition('max-110x110').file

    @cached_property
    def image_small(self):
        if not self.image:
            return None
        return self.get_rendition('max-600x600').file

    @cached_property
    def image_medium(self):
        if not self.image:
            return None
        return self.get_rendition('max-800x800').file

    @cached_property
    def image_large(self):
        if not self.image:
            return None
        return self.get_rendition('max-1600x1600').file

    def is_stored_locally(self):
        """
        Returns True if the image is hosted on the local filesystem
        """
        try:
            self.image.path

            return True
        except NotImplementedError:
            return False

    @contextmanager
    def open_file(self):
        # Open file if it is closed
        close_file = False
        try:
            image_file = self.image

            if self.image.closed:
                # Reopen the file
                if self.is_stored_locally():
                    self.image.open('rb')
                else:
                    # Some external storage backends don't allow reopening
                    # the file. Get a fresh file instance.
                    storage = self._meta.get_field('image').storage
                    image_file = storage.open(self.image.name, 'rb')

                close_file = True
        except IOError as e:
            # re-throw this as a SourceImageIOError so that calling code can distinguish
            # these from IOErrors elsewhere in the process
            raise SourceImageIOError(str(e))

        # Seek to beginning
        image_file.seek(0)

        try:
            yield image_file
        finally:
            if close_file:
                image_file.close()

    @contextmanager
    def get_willow_image(self):
        with self.open_file() as image_file:
            yield WillowImage.open(image_file)

    @classmethod
    def get_rendition_model(cls):
        """ Get the Rendition model for this Image model """
        return cls.renditions.rel.related_model

    def get_rendition(self, filter):
        if isinstance(filter, str):
            filter = Filter(spec=filter)

        cache_key = filter.get_cache_key(self)
        Rendition = self.get_rendition_model()

        try:
            rendition = self.renditions.get(
                filter_spec=filter.spec,
                focal_point_key=cache_key,
            )
        except Rendition.DoesNotExist:
            # Generate the rendition image
            generated_image = filter.run(self, BytesIO())

            # Generate filename
            input_filename = os.path.basename(self.image.name)
            input_filename_without_extension, input_extension = os.path.splitext(input_filename)

            # A mapping of image formats to extensions
            FORMAT_EXTENSIONS = {
                'jpeg': '.jpg',
                'png': '.png',
                'gif': '.gif',
            }

            output_extension = filter.spec.replace('|', '.') + FORMAT_EXTENSIONS[generated_image.format_name]
            if cache_key:
                output_extension = cache_key + '.' + output_extension

            # Truncate filename to prevent it going over 60 chars
            output_filename_without_extension = input_filename_without_extension[:(59 - len(output_extension))]
            output_filename = output_filename_without_extension + '.' + output_extension

            rendition, created = self.renditions.get_or_create(
                filter_spec=filter.spec,
                focal_point_key=cache_key,
                defaults={'file': File(generated_image.f, name=output_filename)}
            )

        return rendition

    def save(self, *args, **kwargs):
        """
        Remove all renditions if the image is removed
        """
        if not self.image:
            self.renditions.all().delete(*args, **kwargs)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Filter:
    """
    Represents one or more operations that can be applied to an Image to produce a rendition
    appropriate for final display on the website. Usually this would be a resize operation,
    but could potentially involve colour processing, etc.
    """

    def __init__(self, spec=None):
        # The spec pattern is operation1-var1-var2|operation2-var1
        self.spec = spec

    @cached_property
    def operations(self):
        # Search for operations
        self._search_for_operations()

        # Build list of operation objects
        operations = []
        for op_spec in self.spec.split('|'):
            op_spec_parts = op_spec.split('-')

            if op_spec_parts[0] not in self._registered_operations:
                raise InvalidFilterSpecError("Unrecognised operation: %s" % op_spec_parts[0])

            op_class = self._registered_operations[op_spec_parts[0]]
            operations.append(op_class(*op_spec_parts))
        return operations

    def run(self, image, output):
        with image.get_willow_image() as willow:
            original_format = willow.format_name

            # Fix orientation of image
            willow = willow.auto_orient()

            env = {
                'original-format': original_format,
            }
            for operation in self.operations:
                willow = operation.run(willow, image, env) or willow

            # Find the output format to use
            if 'output-format' in env:
                # Developer specified an output format
                output_format = env['output-format']
            else:
                # Default to outputting in original format
                output_format = original_format

                # Convert BMP files to PNG
                if original_format == 'bmp':
                    output_format = 'png'

                # Convert unanimated GIFs to PNG as well
                if original_format == 'gif' and not willow.has_animation():
                    output_format = 'png'

            if output_format == 'jpeg':
                # Allow changing of JPEG compression quality
                if 'jpeg-quality' in env:
                    quality = env['jpeg-quality']
                else:
                    quality = 85

                # If the image has an alpha channel, give it a white background
                if willow.has_alpha():
                    willow = willow.set_background_color_rgb((255, 255, 255))

                return willow.save_as_jpeg(output, quality=quality, progressive=True, optimize=True)
            elif output_format == 'png':
                return willow.save_as_png(output, optimize=True)
            elif output_format == 'gif':
                return willow.save_as_gif(output)

    def get_cache_key(self, image):
        vary_parts = []

        for operation in self.operations:
            for field in getattr(operation, 'vary_fields', []):
                value = getattr(image, field, '')
                vary_parts.append(str(value))

        vary_string = '-'.join(vary_parts)

        # Return blank string if there are no vary fields
        if not vary_string:
            return ''

        return hashlib.sha1(vary_string.encode('utf-8')).hexdigest()[:8]

    _registered_operations = None

    @classmethod
    def _search_for_operations(cls):
        if cls._registered_operations is not None:
            return

        operations = [
            ('min', image_operations.MinMaxOperation),
            ('max', image_operations.MinMaxOperation),
            ('width', image_operations.WidthHeightOperation),
            ('height', image_operations.WidthHeightOperation),
        ]

        cls._registered_operations = dict(operations)


class AbstractRendition(models.Model):
    filter_spec = models.CharField(max_length=255, db_index=True)
    file = models.ImageField(upload_to=get_rendition_upload_to, width_field='width', height_field='height')
    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)
    focal_point_key = models.CharField(max_length=16, blank=True, default='', editable=False)

    @property
    def url(self):
        return self.file.url

    @property
    def alt(self):
        return self.image.title

    @property
    def attrs(self):
        """
        The src, width, height, and alt attributes for an <img> tag, as a HTML
        string
        """
        return flatatt(self.attrs_dict)

    @property
    def attrs_dict(self):
        """
        A dict of the src, width, height, and alt attributes for an <img> tag.
        """
        return OrderedDict([
            ('src', self.url),
            ('width', self.width),
            ('height', self.height),
            ('alt', self.alt),
        ])

    def img_tag(self, extra_attributes={}):
        attrs = self.attrs_dict.copy()
        attrs.update(extra_attributes)
        return mark_safe('<img{}>'.format(flatatt(attrs)))

    def __html__(self):
        return self.img_tag()

    def get_upload_to(self, filename):
        folder_name = 'images'
        filename = self.file.field.storage.get_valid_name(filename)
        return os.path.join(folder_name, filename)

    @classmethod
    def check(cls, **kwargs):
        errors = super(AbstractRendition, cls).check(**kwargs)
        if not cls._meta.abstract:
            if not any(
                set(constraint) == set(['image', 'filter_spec', 'focal_point_key'])
                for constraint in cls._meta.unique_together
            ):
                errors.append(
                    checks.Error(
                        "Custom rendition model %r has an invalid unique_together setting" % cls,
                        hint="Custom rendition models must include the constraint "
                        "('image', 'filter_spec', 'focal_point_key') in their unique_together definition.",
                        obj=cls,
                        id='wagtailimages.E001',
                    )
                )

        return errors

    class Meta:
        abstract = True
