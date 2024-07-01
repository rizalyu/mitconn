from django import forms

class AddShopForm(forms.Form):
    shop_url = forms.URLField(label='', required=True, widget=forms.TextInput(attrs={'id': 'url-field'}))