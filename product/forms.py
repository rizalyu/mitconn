from django import forms
from master.models import Shop

class AddProductForm(forms.Form):
    product_url = forms.URLField(label='', required=True, widget=forms.TextInput(attrs={'id': 'url-field'}))
    shop = forms.ModelChoiceField(
        queryset= Shop.objects.all(),
        label='',
        widget=forms.Select(attrs={'id': 'shop-field'})
    )