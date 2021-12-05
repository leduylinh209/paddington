from django.urls import path
from service.facebook import views


urlpatterns = [
    path('no-reply-comments/<page_id>', views.comment),
    path('comment', views.comment_api),
]
