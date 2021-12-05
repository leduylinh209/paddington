from django.contrib import admin
from service.facebook.models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ['comment_id']
