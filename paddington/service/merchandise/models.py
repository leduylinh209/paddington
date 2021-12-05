import uuid

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F

from paddington.images import AbstractRendition, AbtractImage
from paddington.models import TrackingAbstractModel
from service.merchandise.constants import ORDER_STATUS
import json


class Unit(TrackingAbstractModel):
    """
    Unit for a product
    """
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Country(TrackingAbstractModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ['name']


class Brand(AbtractImage, TrackingAbstractModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(null=True, blank=True)

    image = models.ImageField(upload_to="brand/%Y%m%d/%H%M%S/", null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class BrandImageRendition(AbstractRendition):
    """
    Rendition model of a brand image
    """
    image = models.ForeignKey(Brand, related_name='renditions', on_delete=models.CASCADE)

    def get_upload_to(self, filename):
        return "brand/renditions/{}/{}".format(self.image.id, filename)

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)


class Supplier(TrackingAbstractModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class InternalState(TrackingAbstractModel):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Product(TrackingAbstractModel):
    """
    Products are our goods
    """
    sku = models.CharField(max_length=128, unique=True)

    name = models.CharField(max_length=256, db_index=True)
    name_vn = models.CharField(max_length=256, db_index=True, null=True, editable=False)

    short_description = RichTextField(null=True, blank=True)
    long_description = RichTextField(null=True, blank=True)

    rrp = models.PositiveIntegerField(help_text="Recommended retail price in VND",
                                      default=0)
    unit = models.ForeignKey(Unit, null=True, on_delete=models.SET_NULL)

    length = models.PositiveIntegerField(help_text="mm", null=True, blank=True)
    width = models.PositiveIntegerField(help_text="mm", null=True, blank=True)
    height = models.PositiveIntegerField(help_text="mm", null=True, blank=True)
    weight = models.FloatField(help_text="kg", null=True, blank=True)
    volume = models.PositiveIntegerField(help_text="ml", null=True, blank=True)

    product_lifespan = models.CharField(max_length=256, null=True, blank=True)
    packaging_specification = models.CharField(max_length=128, null=True, blank=True)

    origin_text = models.CharField(max_length=128, null=True, blank=True)
    made_in_text = models.CharField(max_length=128, null=True, blank=True)
    brand_text = models.CharField(max_length=128, null=True, blank=True)

    seller = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, default=1)
    origin = models.ForeignKey(Country, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='+')
    made_in = models.ForeignKey(Country, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name='+')
    brand = models.ForeignKey(Brand, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='+')

    internal_state = models.ForeignKey(InternalState, null=True,
                                       on_delete=models.SET_NULL)
    internal_comment = models.TextField(null=True, blank=True)

    shipping_method = models.TextField(null=True, blank=True)
    shipping_time = models.TextField(null=True, blank=True)

    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)

    categories = models.TextField(null=True, editable=False)
    categories_vn = models.TextField(null=True, editable=False)

    all_images = models.TextField(null=True, editable=False)

    def get_all_images(self):
        from service.merchandise.serializers import ImageSerializer
        return json.dumps(ImageSerializer(instance=self.images.all(), many=True).data)

    def __str__(self):
        return "{} ({})".format(self.name, self.sku)


class Image(AbtractImage):
    """
    Image of a product
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images')
    main = models.BooleanField(default=False)
    image = models.ImageField(upload_to="product/%Y%m%d/%H%M%S/")

    importer = models.ForeignKey('merchandise.ProductImageImporter', null=True,
                                 on_delete=models.SET_NULL, editable=False)

    def __str__(self):
        return "Image for product {}".format(self.product)


class ImageRendition(AbstractRendition):
    """
    Rendition model of a image
    """
    image = models.ForeignKey(Image, related_name='renditions', on_delete=models.CASCADE)

    def get_upload_to(self, filename):
        return "product/renditions/{}/{}".format(self.image.id, filename)

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)


class Price(models.Model):
    """
    Pricing policy of a product
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='prices')
    price = models.PositiveIntegerField(help_text="VND")
    max_quantity = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('product', 'max_quantity'),)
        verbose_name = "Pricing policy"
        verbose_name_plural = "Pricing policies"

    def __str__(self):
        return "Price policy for product {}".format(self.product)


class Order(TrackingAbstractModel):
    """
    Model for placing an order
    """
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product, null=True, on_delete=models.SET_NULL,
    )
    # For caching
    product_name = models.CharField(
        max_length=256, null=True, editable=False,
    )

    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text="Price client sent to us")
    amount = models.PositiveIntegerField(editable=False)

    # For cross-checking
    price_by_system = models.PositiveIntegerField(
        help_text="Price calculated by our backend", null=True, editable=False,
    )
    amount_by_system = models.PositiveIntegerField(
        help_text="Amount calculated by our backend", null=True, editable=False,
    )

    deliver_to_me = models.BooleanField()
    receiver_name = models.CharField(max_length=128)
    receiver_phone = models.CharField(max_length=32)
    receiver_address = models.TextField()
    delivery_note = models.TextField(null=True, blank=True)

    collect_on_behalf = models.BooleanField(verbose_name="Cash on delivery")
    collection_money = models.PositiveIntegerField()
    shipping_cost_included = models.BooleanField(
        verbose_name="Customer pays shipping cost",
        default=False,
    )

    client_ip = models.GenericIPAddressField(null=True, editable=False)

    status = models.CharField(choices=ORDER_STATUS, max_length=64, editable=False,
                              default=ORDER_STATUS[0][0], db_index=True)

    ordered_by = models.ForeignKey(User, null=True, blank=True,
                                   on_delete=models.SET_NULL)

    @property
    def ref(self):
        return self.uuid.hex[:6].upper()

    def save(self, *args, **kwargs):
        if self.product:
            self.amount = self.price * self.quantity

            # For caching
            self.product_name = self.product.name

            # For cross-check
            for pp in self.product.prices.order_by(F('max_quantity').asc(nulls_last=True)):
                if pp.max_quantity is None or self.quantity <= pp.max_quantity:
                    self.price_by_system = pp.price
                    self.amount_by_system = pp.price * self.quantity
                    break

        if not self.ordered_by and self.created_by:
            self.ordered_by = self.created_by

        super().save(*args, **kwargs)

    def __str__(self):
        return "Order #{}".format(self.ref)


class OrderStatus(TrackingAbstractModel):
    """
    Status for an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(choices=ORDER_STATUS, max_length=64,
                              default=ORDER_STATUS[0][0])
    internal_comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Order status"
        verbose_name_plural = "Order statuses"


class SamplePost(TrackingAbstractModel):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=512)
    content = models.TextField()
    published = models.BooleanField()

    def __str__(self):
        return "Sample Post #{}: {}".format(self.id, self.product)


class SamplePostImage(AbtractImage):
    sample_post = models.ForeignKey(SamplePost, on_delete=models.CASCADE,
                                    related_name='images')
    main = models.BooleanField(default=False)
    image = models.ImageField(upload_to="sample_post/%Y%m%d/%H%M%S/")

    def __str__(self):
        return "Image for Sample Post {}".format(self.sample_post)


class SamplePostImageRendition(AbstractRendition):
    """
    Rendition model of a sample post image
    """
    image = models.ForeignKey(SamplePostImage, related_name='renditions', on_delete=models.CASCADE)

    def get_upload_to(self, filename):
        return "sample_post/renditions/{}/{}".format(self.image.id, filename)

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)


class TrainingPost(AbtractImage, TrackingAbstractModel):
    """
    Model for training posts
    """
    image = models.ImageField(upload_to="training_post/%Y%m%d/%H%M%S/")
    title = models.CharField(max_length=512)
    content = RichTextUploadingField()
    published = models.BooleanField()

    def __str__(self):
        return "Training Post #{}: {}".format(self.id, self.title)


class TrainingPostImageRendition(AbstractRendition):
    """
    Rendition model of a training post image
    """
    image = models.ForeignKey(TrainingPost, related_name='renditions', on_delete=models.CASCADE)

    def get_upload_to(self, filename):
        return "training_post/renditions/{}/{}".format(self.image.id, filename)

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)


class ProductTrainingPost(models.Model):
    """
    Model for many-to-many relation between Product & TrainingPost
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    training_post = models.ForeignKey(TrainingPost, on_delete=models.CASCADE)

    def __str__(self):
        return "ProductTrainingPost #{}".format(self.id)

    class Meta:
        unique_together = (('product', 'training_post'),)


class Category(AbtractImage, TrackingAbstractModel):
    """
    Model for product categories
    """
    published = models.BooleanField(default=False)

    name = models.CharField(max_length=512)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="category/%Y%m%d/%H%M%S/",
                              null=True, blank=True)

    ordering_score = models.FloatField(default=0)

    def __str__(self):
        return "Category #{}: {}".format(self.id, self.name)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['-ordering_score']


class ParentChildCategory(models.Model):
    child = models.ForeignKey(Category, related_name='parent',
                              on_delete=models.CASCADE)
    parent = models.ForeignKey(Category, related_name='children',
                               on_delete=models.CASCADE)

    def __str__(self):
        return "ParentChildCategory #{}".format(self.id)

    class Meta:
        unique_together = (('parent', 'child'),)
        verbose_name = "Child Category"
        verbose_name_plural = "Child Categories"


class CategoryImageRendition(AbstractRendition):
    """
    Rendition model of a category image
    """
    image = models.ForeignKey(Category, related_name='renditions', on_delete=models.CASCADE)

    def get_upload_to(self, filename):
        return "category/renditions/{}/{}".format(self.image.id, filename)

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)


class ProductCategory(models.Model):
    """
    Model for many-to-many relation between Product & Category
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return "ProductCategory #{}".format(self.id)

    class Meta:
        unique_together = (('product', 'category'),)
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"


class ProductSupplier(models.Model):
    """
    Model for product - supplier relation
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    supplier_price = models.PositiveIntegerField(blank=True, null=True)
    supplier_sku = models.CharField(blank=True, null=True, max_length=128)
    supplier_collection = models.CharField(blank=True, null=True, max_length=256)
    supplier_comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return "ProductSupplier #{}".format(self.id)

    class Meta:
        unique_together = (('product', 'supplier'),)


class ProductImageImporter(TrackingAbstractModel):
    """
    Model for importing images to Product
    """
    zip_file = models.FileField(upload_to="product-image/")

    def __str__(self):
        return "ProductImageImporter #{}".format(self.id)
