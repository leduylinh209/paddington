from dal import autocomplete

from django.contrib.auth.models import User


class CaredByAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()

        qs = User.objects.filter(is_active=True, is_staff=True)

        if self.q:
            qs = qs.filter(username__istartswith=self.q)

        return qs


cared_by_autocomplete = CaredByAutocomplete.as_view()
