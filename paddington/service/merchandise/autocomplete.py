from dal import autocomplete

from service.merchandise.models import Category


class CategoryAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Category.objects.none()

        qs = Category.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


category_autocomplete = CategoryAutocomplete.as_view()
