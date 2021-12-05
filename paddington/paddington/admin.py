"""
This file only contains mixin for ModelAdmin
"""

from reversion.admin import VersionAdmin


class CreatedByAdminMixin(object):

    def save_model(self, request, obj, form, change):
        if obj.id is None:
            obj.created_by = request.user

        if hasattr(obj, 'modified_by'):
            obj.modified_by = request.user

        obj.save()


class TrackingAdminMixin(CreatedByAdminMixin, VersionAdmin):
    """Admin mixin for TrackingAbstractModel,
    this should be put first in inheritant class list, like this

    class FooAdmin(TrackingAdminMixin, admin.ModelAdmin):
        pass
    """
    pass


class ReadOnlyAdminMixin(object):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
