import json

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import truncatewords, truncatewords_html
from django.utils.html import strip_tags
from rest_framework import serializers

from service.merchandise.models import (Category, Image, Order, OrderStatus,
                                        ParentChildCategory, Price, Product,
                                        SamplePost, SamplePostImage,
                                        TrainingPost, Unit)


class ImageSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()
    image_small = serializers.ImageField()
    image_medium = serializers.ImageField()
    image_large = serializers.ImageField()

    class Meta:
        model = Image
        fields = (
            'main', 'image',
            'image_thumbnail', 'image_small', 'image_medium', 'image_large',
        )


class ThumbnailImageSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()

    class Meta:
        model = Image
        fields = (
            'main', 'image_thumbnail',
        )


class SamplePostDetailImageSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()
    image_small = serializers.ImageField()
    image_medium = serializers.ImageField()
    image_large = serializers.ImageField()

    class Meta:
        model = SamplePostImage
        fields = (
            'main', 'image',
            'image_thumbnail', 'image_small', 'image_medium', 'image_large',
        )


class SamplePostListImageSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()

    class Meta:
        model = SamplePostImage
        fields = ('main', 'image_thumbnail')


class PriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Price
        fields = ('price', 'max_quantity')


class GuestPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Price
        fields = ('price', 'max_quantity')


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        fields = ('name', 'code')


class OrderStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderStatus
        fields = ('status', 'created_at')


class SamplePostListSerializer(serializers.ModelSerializer):

    images = serializers.SerializerMethodField()
    desc = serializers.SerializerMethodField()

    def get_images(self, obj):
        # Only get the first or the main image
        return [
            SamplePostListImageSerializer(
                instance=obj.images.order_by('-main').first(),
                context=self.context,
            ).data
        ]

    def get_desc(self, obj):
        return truncatewords(obj.content, 20)

    class Meta:
        model = SamplePost
        fields = ('id', 'title', 'desc', 'images')


class SamplePostDetailSerializer(serializers.ModelSerializer):

    images = SamplePostDetailImageSerializer(many=True)

    class Meta:
        model = SamplePost
        fields = ('id', 'title', 'content', 'images')


class CategoryListSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'image_thumbnail')


class CategoryDetailSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        # TODO: Limit this
        return CategoryListSerializer(
            instance=Category.objects.filter(
                id__in=ParentChildCategory.objects.filter(
                    parent_id=obj.id
                ).values_list('child_id'),
                published=True,
            ),
            context=self.context,
            many=True,
        ).data

    class Meta:
        model = Category
        fields = ('id', 'name', 'image_thumbnail', 'description', 'children')


class ProductListSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True)
    unit = UnitSerializer(read_only=True)
    unit_id = serializers.IntegerField(write_only=True)

    images = serializers.SerializerMethodField()
    samplepost_set = serializers.SerializerMethodField()
    trainingpost_count = serializers.SerializerMethodField()
    samplepost_count = serializers.SerializerMethodField()

    brand = serializers.SerializerMethodField()
    origin = serializers.SerializerMethodField()
    made_in = serializers.SerializerMethodField()

    def get_images(self, obj):
        if not obj.all_images:
            return []

        try:
            all_images = json.loads(obj.all_images)
        except Exception:
            return []

        request = self.context.get('request', None)
        if request is not None:
            return [
                {
                    'main': image.get('main', False),
                    'image': request.build_absolute_uri(image.get('image', '/')),
                    'image_thumbnail': request.build_absolute_uri(image.get('image_thumbnail', '/')),
                    'image_small': request.build_absolute_uri(image.get('image_small', '/')),
                    'image_medium': request.build_absolute_uri(image.get('image_medium', '/')),
                    'image_large': request.build_absolute_uri(image.get('image_large', '/')),
                }
                for image in all_images
            ]
        return all_images

    def get_brand(self, obj):
        return obj.brand and obj.brand.name

    def get_made_in(self, obj):
        return obj.made_in and obj.made_in.name

    def get_origin(self, obj):
        return obj.origin and obj.origin.name

    def get_samplepost_set(self, obj):
        # TODO: Remove this
        return []

    def get_trainingpost_count(self, obj):
        return TrainingPost.objects.filter(
            published=True,
            producttrainingpost__product_id=obj.id,
        ).count()

    def get_samplepost_count(self, obj):
        return SamplePost.objects.filter(
            published=True,
            product_id=obj.id,
        ).count()

    def get_unit(self, obj):
        return obj.get_unit_display()

    def create(self, validated_data):
        prices_data = validated_data.pop('prices')
        # unit_data = validated_data.pop('unit')
        product = Product.objects.create(**validated_data)

        prices_selializer = self.fields['prices']
        for price in prices_data:
            price['product'] = product
        prices = prices_selializer.create(prices_data)

        # unit, created = Unit.objects.get_or_create(code=unit_data['code'], defaults={'name': unit_data['name']})
        # product.unit = unit
        # product.save()
        return product

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'featured', 'published',
            'images', 'prices', 'samplepost_set', 'trainingpost_count', 'samplepost_count',
            'unit', 'unit_id', 'rrp', 'sku',
            'shipping_method', 'shipping_time', 'short_description',
            'brand', 'origin', 'made_in',
            'length', 'width', 'height', 'volume', 'weight', 'packaging_specification',
            'product_lifespan',
            'long_description',
        )


class GuestProductSerializer(ProductListSerializer):

    prices = GuestPriceSerializer(many=True)


class ProductDetailSerializer(ProductListSerializer):
    category_set = serializers.SerializerMethodField()

    def get_samplepost_set(self, obj):
        # TODO: Remove this
        return []

    def get_category_set(self, obj):
        # TODO: Limit this queryset
        return CategoryListSerializer(
            instance=Category.objects.filter(
                published=True,
                id__in=obj.productcategory_set.filter(
                    product_id=obj.id
                ).values_list('category_id')
            ),
            many=True,
            context=self.context,
        ).data

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'featured', 'category_set',
            'images', 'prices', 'samplepost_set', 'trainingpost_count', 'samplepost_count',
            'unit', 'rrp', 'sku',
            'shipping_method', 'shipping_time', 'short_description',
            'brand', 'origin', 'made_in',
            'length', 'width', 'height', 'volume', 'weight', 'packaging_specification',
            'product_lifespan',
            'long_description',
        )


class GuestProductDetailSerializer(ProductDetailSerializer):

    prices = GuestPriceSerializer(many=True)


class RelatedProductSerializer(serializers.ModelSerializer):
    images = ThumbnailImageSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'images',
        )


class OrderSerializer(serializers.ModelSerializer):
    uuid = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()
    product_name = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()

    orderstatus_set = OrderStatusSerializer(many=True, read_only=True)

    product_id = serializers.IntegerField(write_only=True)
    product = ProductListSerializer(read_only=True)
    ref = serializers.SerializerMethodField()

    def get_ref(self, obj):
        return obj.ref

    class Meta:
        model = Order
        fields = (
            'uuid', 'created_at', 'ref', 'status', 'orderstatus_set',
            'product_name', 'product_id', 'product',
            'quantity', 'price', 'amount', 'deliver_to_me', 'receiver_name', 'receiver_phone',
            'receiver_address', 'delivery_note', 'collect_on_behalf', 'collection_money',
            'shipping_cost_included',
        )


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class TrainingPostListSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()
    image_small = serializers.ImageField()
    image_medium = serializers.ImageField()
    image_large = serializers.ImageField()

    desc = serializers.SerializerMethodField()

    def get_desc(self, obj):
        return strip_tags(truncatewords_html(obj.content, 20))

    class Meta:
        model = TrainingPost
        fields = (
            'id', 'title', 'desc',
            'image_thumbnail', 'image_small', 'image_medium', 'image_large',
        )


class TrainingPostDetailSerializer(serializers.ModelSerializer):

    image_thumbnail = serializers.ImageField()
    image_small = serializers.ImageField()
    image_medium = serializers.ImageField()
    image_large = serializers.ImageField()

    created_by = AuthorSerializer()
    products = serializers.SerializerMethodField()

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        request = self.context.get('request', None)
        if request is not None:
            return obj.content.replace(
                settings.MEDIA_URL,
                request.build_absolute_uri(settings.MEDIA_URL),
            )
        return obj.content

    def get_products(self, obj):
        # TODO: Limit this queryset
        return RelatedProductSerializer(
            instance=Product.objects.filter(
                id__in=obj.producttrainingpost_set.filter(
                    training_post_id=obj.id,
                    product__published=True,
                ).values_list('product_id')
            ),
            many=True,
            context=self.context,
        ).data

    class Meta:
        model = TrainingPost
        fields = (
            'id', 'title', 'content', 'modified_at', 'created_by',
            'image_thumbnail', 'image_small', 'image_medium', 'image_large',
            'products',
        )
