from account import views
from django.urls import path
from account import autocomplete


urlpatterns = [
    # Register
    path("new/", views.register_view),
    # Friends
    path("friend/", views.friend_view),
    # Transactions
    path("transaction/", views.transaction_view),
    # Notifications
    path("notification/", views.notification_list_view),
    path("notification/<int:pk>/", views.notification_detail_view),
    # Autocomplete views
    path(
        "user-autocomplete/",
        autocomplete.cared_by_autocomplete,
        name="user-autocomplete",
    ),
    # Verification
    path("send-otp/", views.send_otp_view),
    path("verify-otp/", views.verify_otp_view)
]
