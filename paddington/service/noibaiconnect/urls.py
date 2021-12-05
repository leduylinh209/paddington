from django.urls import path
from service.noibaiconnect import views


urlpatterns = [
    path('quotation/', views.quotation),    # Get price for each route
    path('booking/', views.booking),        # Book a ticket
]
