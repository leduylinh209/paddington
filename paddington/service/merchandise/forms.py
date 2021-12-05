from django import forms
from dal import autocomplete

from service.merchandise.models import Category, Product, ProductCategory


class AddCategoryForm(forms.Form):

    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    product_list = forms.CharField(widget=forms.HiddenInput)
    to_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=autocomplete.ModelSelect2(url='category-autocomplete')
    )

    def save(self, commit=True):
        product_list_ids = self.cleaned_data.get('product_list', '').split(',')
        to_category = self.cleaned_data.get('to_category', None)

        if to_category and product_list_ids:
            product_list = Product.objects.filter(id__in=product_list_ids)
            for product in product_list:
                ProductCategory.objects.get_or_create(
                    product=product,
                    category=to_category,
                )
                product.save()  # Trigger signals
