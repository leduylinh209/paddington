from django.contrib import admin
from django import forms

from paddington.admin import TrackingAdminMixin
from service.store.models import AppRelease


class AppReleaseForm(forms.ModelForm):
    stores = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                       choices=[
                                           ('itunes', 'iOS App Store'),
                                           ('play', 'Google Play'),
                                       ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        obj = kwargs.get('instance')
        if obj:
            self.initial['stores'] = obj.stores.split(',')

    def clean_stores(self):
        return ','.join(self.cleaned_data.get('stores', []))

    class Meta:
        model = AppRelease
        exclude = ()


@admin.register(AppRelease)
class AppReleaseAdmin(TrackingAdminMixin):
    form = AppReleaseForm
    list_display = ['id', 'version', 'release_note', 'stores', 'created_at', 'created_by']
    list_display_links = ['id', 'version']
    readonly_fields = ['created_at', 'created_by', 'modified_at', 'modified_by']
