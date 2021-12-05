from django import forms
from dal import autocomplete

from django.contrib.auth.models import User


class AddCaredByForm(forms.Form):

    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    user_list = forms.CharField(widget=forms.HiddenInput)
    cared_by = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True, is_staff=True),
        widget=autocomplete.ModelSelect2(url='user-autocomplete')
    )

    def save(self, commit=True):
        user_list_ids = self.cleaned_data.get('user_list', '').split(',')
        cared_by = self.cleaned_data.get('cared_by', None)

        if cared_by and user_list_ids:
            for user in User.objects.filter(id__in=user_list_ids):
                if hasattr(user, 'profile'):
                    user.profile.cared_by = cared_by
                    user.profile.save_without_signals()
