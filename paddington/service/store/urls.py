from django.urls import path
from service.store import views


urlpatterns = [
    path('version/', views.version),    # Check app version from Play store & App store
    path('release/', views.release),    # Check app version from our server
]
