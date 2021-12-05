from django.contrib.postgres.search import (SearchQuery, SearchRank,
                                            SearchVector)
from django.shortcuts import get_object_or_404
from ipware import get_client_ip
from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from service.merchandise.models import (Category, Order, ParentChildCategory,
                                        Product, SamplePost, TrainingPost)
from service.merchandise.serializers import (CategoryDetailSerializer,
                                             CategoryListSerializer,
                                             GuestProductDetailSerializer,
                                             GuestProductSerializer,
                                             OrderSerializer,
                                             ProductDetailSerializer,
                                             ProductListSerializer,
                                             SamplePostDetailSerializer,
                                             SamplePostListSerializer,
                                             TrainingPostDetailSerializer,
                                             TrainingPostListSerializer)
from service.merchandise.tasks import (create_new_communication,
                                       slack_hook_new_order)


class ProductListAPI(generics.ListCreateAPIView):
    """
    API for booking a trip
    """
    queryset = Product.objects.filter(published=True).order_by('-featured')
    serializer_class = ProductListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ProductListSerializer
        return GuestProductSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category_id')
        q = self.request.query_params.get('q')
        exclude = self.request.query_params.get('exclude')

        queryset = super().get_queryset()

        # Filter by category
        if category_id:
            # TODO: Use another relation kind that's more efficient
            category_ids = list(ParentChildCategory.objects.filter(
                parent_id=category_id,
                child__published=True,
            ).values_list('child_id')) + [category_id]

            queryset = queryset.filter(
                productcategory__category_id__in=category_ids,
            )

        # Searching
        if q:
            vector = SearchVector(
                'sku',
                'name', 'name_vn',
                'categories', 'categories_vn',
            )
            query = SearchQuery(q)
            queryset = queryset.annotate(
                rank=SearchRank(vector, query)
            ).filter(rank__gte=0.001).order_by('-rank')

        # Exclude product
        if exclude:
            queryset = queryset.exclude(id=exclude)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Attach category info
        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            category = get_object_or_404(Category,
                                         id=category_id,
                                         published=True)
            response.data['category'] = CategoryDetailSerializer(
                category,
                context=self.get_serializer_context(),
            ).data

        return response


class ProductDetailAPI(generics.RetrieveAPIView):
    """
    API for booking a trip
    """
    queryset = Product.objects.filter(published=True)
    serializer_class = ProductDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ProductDetailSerializer
        return GuestProductDetailSerializer


class OrderListAPI(generics.ListCreateAPIView):
    """
    API for listing & creating orders
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(ordered_by=self.request.user).order_by('-id')

    def post(self, request, *args, **kwargs):
        order_serializer = OrderSerializer(data=request.data)
        order_serializer.is_valid(raise_exception=True)

        client_ip, _ = get_client_ip(request)
        order = order_serializer.save(
            created_by=request.user,
            client_ip=client_ip,
        )
        resp = OrderSerializer(order).data

        # Only attach id for slack hook
        booking_data = resp.copy()
        booking_data["id"] = order.id
        booking_data["created_by"] = order.created_by_id

        slack_hook_new_order.delay(booking_data)
        create_new_communication.delay(booking_data)

        return Response(resp)


class OrderDetailAPI(generics.RetrieveUpdateAPIView):
    """
    API for listing & creating orders
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'

    def get_queryset(self):
        return super().get_queryset().filter(ordered_by=self.request.user)


class SamplePostListAPI(generics.ListAPIView):
    """
    API for viewing sample post list
    """
    queryset = SamplePost.objects.filter(published=True).order_by('-id')
    serializer_class = SamplePostListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id', None)
        queryset = super().get_queryset()
        if product_id:
            return queryset.filter(product_id=product_id)
        return queryset


class SamplePostDetailAPI(generics.RetrieveAPIView):
    """
    API for viewing sample post detail
    """
    queryset = SamplePost.objects.filter(published=True).order_by('-id')
    serializer_class = SamplePostDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]


class TrainingPostListAPI(generics.ListAPIView):
    """
    API for viewing training post list
    """
    queryset = TrainingPost.objects.filter(published=True).order_by('-modified_at')
    serializer_class = TrainingPostListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id', None)
        queryset = super().get_queryset()
        if product_id:
            return queryset.filter(producttrainingpost__product_id=product_id)
        return queryset


class TrainingPostDetailAPI(generics.RetrieveAPIView):
    """
    API for viewing training post detail
    """
    queryset = TrainingPost.objects.filter(published=True)
    serializer_class = TrainingPostDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]


class CategoryListAPI(generics.ListAPIView):
    """
    API for viewing category list
    """
    queryset = Category.objects.filter(
        published=True,
        parent__isnull=True,
    )
    serializer_class = CategoryListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]


product_list = ProductListAPI.as_view()
product_detail = ProductDetailAPI.as_view()

order_list = OrderListAPI.as_view()
order_detail = OrderDetailAPI.as_view()

sample_post_list = SamplePostListAPI.as_view()
sample_post_detail = SamplePostDetailAPI.as_view()

training_post_list = TrainingPostListAPI.as_view()
training_post_detail = TrainingPostDetailAPI.as_view()

category_list = CategoryListAPI.as_view()
