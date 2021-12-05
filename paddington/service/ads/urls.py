from django.urls import path
from service.ads import views


urlpatterns = [
    path('block_ip', views.block_ip),
    path('unblock_ip', views.unblock_ip),
]
