from django.urls import path, include

urlpatterns = [
    path('nbc/', include('service.noibaiconnect.urls')),
    path('app/', include('service.store.urls')),
    path('product/', include('service.merchandise.urls')),
    path('ads/', include('service.ads.urls')),
    path('fb/', include('service.facebook.urls')),
]
