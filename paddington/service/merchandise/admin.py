from django.contrib import admin, messages
from django.db.models import Count
from django.shortcuts import redirect, render, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export.admin import ImportMixin
from reversion.admin import VersionAdmin

from paddington.admin import TrackingAdminMixin
from service.merchandise.forms import AddCategoryForm
from service.merchandise.models import (Brand, Category, Country, Image,
                                        InternalState, Order, OrderStatus,
                                        ParentChildCategory, Price, Product,
                                        ProductCategory, ProductImageImporter,
                                        ProductSupplier, ProductTrainingPost,
                                        SamplePost, SamplePostImage, Supplier,
                                        TrainingPost, Unit)
from service.merchandise.resource import ProductResource, PriceResource


class ImageInlineAdmin(admin.TabularInline):
    model = Image
    extra = 0
    readonly_fields = ('thumbnail', 'importer_')
    fields = ('main', 'image', 'thumbnail', 'importer_')

    def get_formset(self, request, *args, **kwargs):
        formset = super().get_formset(request, *args, **kwargs)
        self.request = request
        return formset

    def importer_(self, obj):
        url = reverse('admin:merchandise_productimageimporter_change',
                      args=(obj.importer_id,))
        if obj.importer_id:
            return format_html(
                '<a href="{}" target="_blank">ProductImageImporter #{}</a>', url, obj.importer_id
            )
        return ''

    def thumbnail(self, obj):
        if not obj.image:
            return ""

        image_url = ""
        try:
            image_url = mark_safe("""<img src="{}" />""".format(
                obj.image_thumbnail.url
            ))
        except Exception as e:
            messages.add_message(self.request, messages.ERROR, e)

        return image_url


class SamplePostImageInlineAdmin(admin.TabularInline):
    model = SamplePostImage
    extra = 0
    readonly_fields = ('thumbnail',)
    fields = ('main', 'image', 'thumbnail')

    def get_formset(self, request, *args, **kwargs):
        formset = super().get_formset(request, *args, **kwargs)
        self.request = request
        return formset

    def thumbnail(self, obj):
        if not obj.image:
            return ""

        image_url = ""
        try:
            image_url = mark_safe("""<img src="{}" />""".format(
                obj.image_thumbnail.url)
            )
        except Exception as e:
            messages.add_message(self.request, messages.ERROR, e)

        return image_url


class ProductTrainingPostInlineAdmin(admin.TabularInline):
    model = ProductTrainingPost
    extra = 0
    max_num = 0
    can_delete = False
    fields = readonly_fields = ('product', 'training_post', 'training_post_link')

    autocomplete_lookup_fields = {
        'fk': ['training_post']
    }
    raw_id_fields = ['training_post']

    def training_post_link(self, obj):
        url = reverse('admin:merchandise_trainingpost_change',
                      args=(obj.training_post_id,))
        if obj.training_post_id:
            return format_html(
                '<a href="{}" target="_blank">TrainingPost #{}</a>', url, obj.training_post_id
            )
        return ''


class TrainingPostProductInlineAdmin(admin.TabularInline):
    model = ProductTrainingPost
    extra = 0
    readonly_fields = ('training_post', 'product_link')
    fields = ('product', 'training_post', 'product_link')

    autocomplete_lookup_fields = {
        'fk': ['product']
    }
    raw_id_fields = ['product']

    def product_link(self, obj):
        url = reverse('admin:merchandise_product_change',
                      args=(obj.product_id,))
        if obj.product_id:
            return format_html(
                '<a href="{}" target="_blank">Product #{}</a>', url, obj.product_id
            )
        return ''


class PriceInlineAdmin(admin.TabularInline):
    model = Price
    extra = 0
    min_num = 0
    fields = ('price', 'max_quantity')


class ParentChildCategoryInlineAdmin(admin.TabularInline):
    fk_name = "parent"
    model = ParentChildCategory
    extra = 0
    readonly_fields = ('parent',)
    fields = ('parent', 'child')

    autocomplete_lookup_fields = {
        'fk': ['child']
    }
    raw_id_fields = ['child']


class ChildParentCategoryInlineAdmin(admin.TabularInline):
    verbose_name = "Parent Category"
    verbose_name_plural = "Parent Category"

    fk_name = "child"
    model = ParentChildCategory
    extra = 0
    max_num = 1
    readonly_fields = ('child',)
    fields = ('parent', 'child')

    autocomplete_lookup_fields = {
        'fk': ['parent']
    }
    raw_id_fields = ['parent']


class ProductCategoryInlineAdmin(admin.TabularInline):
    model = ProductCategory
    extra = 0
    readonly_fields = ('product', 'category_link')
    fields = ('product', 'category', 'category_link')

    autocomplete_lookup_fields = {
        'fk': ['category']
    }
    raw_id_fields = ['category']

    def category_link(self, obj):
        url = reverse('admin:merchandise_category_change',
                      args=(obj.category_id,))
        if obj.category_id:
            return format_html(
                '<a href="{}" target="_blank">Category #{}</a>', url, obj.category_id
            )
        return ''


class ProductSupplierInlineAdmin(admin.TabularInline):
    model = ProductSupplier
    extra = 0
    readonly_fields = ('product', 'supplier_link')
    fields = (
        'product', 'supplier', 'supplier_link',
        'supplier_price', 'supplier_sku', 'supplier_collection', 'supplier_comment',
    )

    autocomplete_lookup_fields = {
        'fk': ['supplier']
    }
    raw_id_fields = ['supplier']

    def supplier_link(self, obj):
        url = reverse('admin:merchandise_supplier_change',
                      args=(obj.supplier_id,))
        if obj.category_id:
            return format_html(
                '<a href="{}" target="_blank">Supplier #{}</a>', url, obj.supplier_id
            )
        return ''


class SamplePostInlineAdmin(admin.TabularInline):
    model = SamplePost
    fields = readonly_fields = ('id', 'title', 'sample_post_link')
    extra = 0
    max_num = 0
    can_delete = False

    def sample_post_link(self, obj):
        url = reverse('admin:merchandise_samplepost_change',
                      args=(obj.id,))
        if obj.id:
            return format_html(
                '<a href="{}" target="_blank">SamplePost #{}</a>', url, obj.id
            )
        return ''


@admin.register(Unit)
class UnitAdmin(VersionAdmin):
    pass


class OrderStatusInlineAdmin(admin.TabularInline):
    readonly_fields = ('created_by', 'created_at', 'modified_by', 'modified_at')
    fields = ('status', 'internal_comment') + readonly_fields
    model = OrderStatus
    extra = 0
    min_num = 0
    can_delete = False

    def has_change_permission(self, request, obj=None):
        # Only super user can change old statuses for now
        return request.user.is_superuser


class InternalStateFilter(admin.SimpleListFilter):
    title = 'Internal state'
    parameter_name = 'internal_state'

    def lookups(self, request, model_admin):
        return [
            (s.id, s.name)
            for s in InternalState.objects.order_by('name')
        ]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(
                internal_state_id=self.value()
            )

        return queryset


class SamplePostCountFilter(admin.SimpleListFilter):
    title = 'Sample post count'
    parameter_name = 'sample_post_count'

    def lookups(self, request, model_admin):
        return [
            ('0', '0'),
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('>5', '>5'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.annotate(sample_post_count=Count('samplepost'))
            if self.value().isdigit():
                queryset = queryset.filter(sample_post_count=int(self.value()))
            else:
                queryset = queryset.filter(sample_post_count__gt=int(self.value()[1:]))

        return queryset


@admin.register(Product)
class ProductAdmin(ImportMixin, TrackingAdminMixin):
    list_display = ['id', 'name', 'sku', 'modified_at', 'modified_by', 'published',
                    'sample_post_count', 'training_post_count', 'categories',
                    'internal_state']
    list_display_links = ['id', 'name']
    inlines = [ImageInlineAdmin, PriceInlineAdmin, SamplePostInlineAdmin,
               ProductTrainingPostInlineAdmin, ProductCategoryInlineAdmin,
               ProductSupplierInlineAdmin]
    readonly_fields = ['created_at', 'created_by', 'modified_at', 'modified_by',
                       'categories']
    list_filter = ['productcategory__category_id', InternalStateFilter,
                   SamplePostCountFilter]
    search_fields = ['name', 'sku',
                     'short_description', 'long_description']

    actions = ['add_category', 'publish', 'unpublish']

    autocomplete_lookup_fields = {
        'fk': ['made_in', 'origin', 'brand']
    }
    raw_id_fields = ['made_in', 'origin', 'brand']

    resource_class = ProductResource

    change_list_template = 'admin/merchandise/product/change_list.html'

    fieldsets = (
        ('Summary', {
            'fields': (
                'published', 'seller', 'sku', 'name', 'featured', 'internal_state',
                'internal_comment',
            ),
        }),
        ('Description', {
            'fields': (
                'short_description', 'long_description',
            ),
        }),
        ('Price', {
            'fields': (
                ('rrp', 'unit'),
            ),
        }),
        ('Measurement', {
            'fields': (
                ('length', 'width', 'height'),
                ('weight', 'volume'),
                'packaging_specification',
            ),
        }),
        ('Extra', {
            'fields': (
                'product_lifespan',
                ('origin', 'made_in'),
                'brand'
            ),
        }),
        ('Ship', {
            'fields': (
                'shipping_method', 'shipping_time',
            ),
        }),
        ('System', {
            'fields': (
                ('created_at', 'created_by'),
                ('modified_at', 'modified_by'),
            ),
        }),
    )

    def add_category(self, request, queryset):
        # POST
        if request.POST.get('save'):
            add_category_form = AddCategoryForm(request.POST)

            if add_category_form.is_valid():
                add_category_form.save(commit=True)
                messages.info(
                    request,
                    "Added category to {} product(s)".format(queryset.count()),
                )
                return redirect(request.get_full_path())

            errors_list = [add_category_form.errors]
            messages.add_message(
                request,
                messages.ERROR,
                "\n".join(
                    "\n".join(value)
                    for d in errors_list
                    for value in d.values()
                    if d
                )
            )

        # GET
        product_list = ','.join([str(p.id) for p in queryset])
        add_category_form = AddCategoryForm(initial={
            'product_list': product_list,
            '_selected_action': request.POST.getlist(
                admin.ACTION_CHECKBOX_NAME),
        })

        return render(
            request,
            'admin/merchandise/product/add_category.html',
            {
                'opts': self.model._meta,
                'has_change_permission': True,
                'form': add_category_form,
                'title': 'Add products to a category',
            }
        )

    add_category.short_description = "Add a category to these products"

    def publish(self, request, queryset):
        queryset.update(published=True)
        messages.info(request, "Published {} product(s)".format(queryset.count()))

    publish.short_description = "Publish these products"

    def unpublish(self, request, queryset):
        queryset.update(published=False)
        messages.info(request, "Unpublished {} product(s)".format(queryset.count()))

    unpublish.short_description = "Unpublish these products"

    def sample_post_count(self, obj):
        return obj.samplepost_set.count()

    def training_post_count(self, obj):
        return obj.producttrainingpost_set.count()

    def categories(self, obj):
        return ", ".join(pc.category.name for pc in obj.productcategory_set.all())

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Trigger post_save install after saving all related fields
        form.instance.save()


class NeedActionOrderFilter(admin.SimpleListFilter):
    title = 'Need Action'
    parameter_name = 'need_action'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Yes'),
            ('no', 'No'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            queryset = queryset.filter(
                status__in=[
                    "new", "confirmed", "ready_to_ship", "dispatched",
                    "shipping", "delivered", "problem",
                ]
            )
        elif self.value() == 'no':
            queryset = queryset.filter(
                status__in=["completed", "cancelled"]
            )

        return queryset


@admin.register(Order)
class OrderAdmin(TrackingAdminMixin):
    change_list_template = "admin/change_list_filter_sidebar.html"

    list_display = [
        '__str__', 'status', 'product_name', 'quantity', 'amount', 'collection_money',
        'ordered_by', 'receiver_address', 'created_at', 'modified_at',
    ]
    inlines = [OrderStatusInlineAdmin]
    search_fields = ['uuid', 'receiver_name', 'receiver_address',
                     'created_by__username']
    list_filter = ['status', NeedActionOrderFilter]
    list_display_links = ['__str__']
    readonly_fields = [
        'ref', 'uuid', 'status', 'amount', 'price_by_system', 'amount_by_system',
        'product_name', 'created_at', 'created_by', 'client_ip',
    ]

    autocomplete_lookup_fields = {
        'fk': ['ordered_by', 'product']
    }
    raw_id_fields = ['ordered_by', 'product']

    fieldsets = (
        ('Order', {
            'fields': (
                'ref', 'status', 'uuid',
            ),
        }),
        ('Product', {
            'fields': (
                'product',
                'product_name',
                'quantity',
                ('price', 'price_by_system'),
                ('amount', 'amount_by_system'),
                'collect_on_behalf',
                'collection_money',
                'shipping_cost_included',
            ),
        }),
        ('Delivery', {
            'fields': (
                'deliver_to_me',
                'receiver_name', 'receiver_phone', 'receiver_address',
                'delivery_note',
            ),
        }),
        ('Status', {
            'classes': ('placeholder orderstatus_set-group',),
            'fields': (),
        }),
        ('System', {
            'fields': (
                'ordered_by',
                ('created_at', 'created_by', 'client_ip'),
            ),
        }),
    )


@admin.register(SamplePost)
class SamplePostAdmin(TrackingAdminMixin):
    list_display = ['id', 'title', 'product_link', 'modified_at', 'modified_by', 'published']
    list_display_links = ['id', 'title']
    inlines = [SamplePostImageInlineAdmin]
    readonly_fields = ['created_at', 'created_by', 'modified_at', 'modified_by', 'product_link']
    search_fields = ['title', 'content']

    autocomplete_lookup_fields = {
        'fk': ['product']
    }
    raw_id_fields = ['product']

    fieldsets = (
        ('Content', {
            'fields': (
                'published', 'title', 'content',
                'product', 'product_link',
            ),
        }),
        ('System', {
            'fields': (
                ('created_at', 'created_by'),
                ('modified_at', 'modified_by'),
            ),
        }),
    )

    def product_link(self, obj):
        url = reverse('admin:merchandise_product_change',
                      args=(obj.product_id,))
        if obj.product_id:
            return format_html(
                '<a href="{}" target="_blank">Product #{}</a>', url, obj.product_id
            )
        return ''


@admin.register(TrainingPost)
class TrainingPostAdmin(TrackingAdminMixin):
    list_display = ['id', 'title', 'product_links', 'modified_at', 'modified_by', 'published']
    list_display_links = ['id', 'title']
    inlines = [TrainingPostProductInlineAdmin]
    readonly_fields = ['created_at', 'created_by', 'modified_at', 'modified_by',
                       'product_links', 'thumbnail']
    search_fields = ['title', 'content']

    fieldsets = (
        ('Settings', {
            'fields': (
                'published',
            ),
        }),
        ('Content', {
            'fields': (
                'title',
                ('image', 'thumbnail'),
                'content',
            ),
        }),
        ('Training posts', {
            'classes': ('placeholder producttrainingpost_set-group',),
            'fields': (),
        }),
        ('Categories', {
            'classes': ('placeholder productcategory_set-group',),
            'fields': (),
        }),
        ('System', {
            'fields': (
                ('created_at', 'created_by'),
                ('modified_at', 'modified_by'),
            ),
        }),
    )

    def product_links(self, obj):
        return format_html(
            ', '.join([
                '<a href="{}" target="_blank">Product #{}</a>'.format(
                    reverse('admin:merchandise_product_change', args=(p.product_id,)),
                    p.product_id,
                )
                for p in obj.producttrainingpost_set.all()
            ])
        )

    def thumbnail(self, obj):
        if not obj.image:
            return ""

        image_url = ""
        try:
            image_url = mark_safe("""<img src="{}" />""".format(
                obj.image_thumbnail.url)
            )
        except Exception as e:
            messages.add_message(self.request, messages.ERROR, e)

        return image_url


@admin.register(Category)
class CategoryAdmin(TrackingAdminMixin):
    list_display = ['id', 'name', 'product_count',
                    'modified_at', 'modified_by', 'created_at', 'published',
                    'ordering_score']
    list_display_links = ['id', 'name']
    inlines = [ParentChildCategoryInlineAdmin, ChildParentCategoryInlineAdmin]
    readonly_fields = ['created_at', 'created_by', 'modified_at', 'modified_by',
                       'thumbnail', 'product_link', 'product_count']
    search_fields = ['title', 'content']

    fieldsets = (
        ('Content', {
            'fields': (
                'published', 'name',
                ('image', 'thumbnail'),
                'description',
                'ordering_score',
                'product_link',
            ),
        }),
        ('Parent', {
            'classes': ('placeholder parent-group',),
            'fields': (),
        }),
        ('Children', {
            'classes': ('placeholder children-group',),
            'fields': (),
        }),
        ('System', {
            'fields': (
                ('created_at', 'created_by'),
                ('modified_at', 'modified_by'),
            ),
        }),
    )

    def thumbnail(self, obj):
        if not obj.image:
            return ""
        return mark_safe("""<img src="{}" />""".format(obj.image_thumbnail.url))

    def product_link(self, obj):
        url = "{}?productcategory__category_id={}".format(
            reverse('admin:merchandise_product_changelist'),
            obj.id,
        )
        if obj.id:
            return format_html(
                '<a href="{}" target="_blank">Products in category: {}</a>', url, obj.name,
            )
        return ''

    def product_count(self, obj):
        return obj.productcategory_set.count()


@admin.register(Country)
class CountryAdmin(TrackingAdminMixin):
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(TrackingAdminMixin):
    search_fields = ['name']
    fields = ['code', 'name', 'description', 'image', 'thumbnail']
    readonly_fields = ['thumbnail']

    def thumbnail(self, obj):
        if not obj.image:
            return ""
        return mark_safe("""<img src="{}" />""".format(obj.image_thumbnail.url))


@admin.register(Supplier)
class SupplierAdmin(TrackingAdminMixin):
    pass


@admin.register(InternalState)
class InternalStateAdmin(TrackingAdminMixin):
    pass


@admin.register(ProductImageImporter)
class ProductImageImporterAdmin(TrackingAdminMixin):
    pass


@admin.register(Price)
class PriceAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = PriceResource

    autocomplete_lookup_fields = {
        'fk': ['product']
    }
    raw_id_fields = ['product']

    list_display = fields = ['product', 'price', 'max_quantity']
