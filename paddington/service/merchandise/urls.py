from django.urls import path
from service.merchandise import views
from service.merchandise import autocomplete


urlpatterns = [
    # API views
    path('list/', views.product_list),
    path('list/<int:pk>/', views.product_detail),

    path('order/', views.order_list),
    path('order/<uuid:uuid>/', views.order_detail),

    path('post/<int:pk>/', views.sample_post_detail),

    path('sample-post/', views.sample_post_list),
    path('sample-post/<int:pk>/', views.sample_post_detail),

    path('training-post/', views.training_post_list),
    path('training-post/<int:pk>/', views.training_post_detail),

    path('category/', views.category_list),

    # Autocomplete views
    path('category-autocomplete/',
         autocomplete.category_autocomplete,
         name='category-autocomplete'),
]
