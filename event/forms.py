from django import forms
from master.models import Product

class AddEventForm(forms.Form):
    event_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'text-field', 'id': 'event-name-field'}))
    start_date = forms.DateTimeField(required=True,  widget=forms.DateTimeInput(attrs={'class': 'text-field', 'id': 'event-startdate-field', 'type': 'datetime-local'}))
    end_date = forms.DateTimeField(required=True,  widget=forms.DateTimeInput(attrs={'class': 'text-field', 'id': 'event-enddate-field', 'type': 'datetime-local'}))

class EditEventForm(forms.Form):
    event_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'text-field'}))
    start_date = forms.DateTimeField(required=True,  widget=forms.DateTimeInput(attrs={'class': 'text-field', 'type': 'datetime-local'}))
    end_date = forms.DateTimeField(required=True,  widget=forms.DateTimeInput(attrs={'class': 'text-field', 'type': 'datetime-local'}))

class AddEventParticipantForms(forms.Form):
    participant = forms.ModelChoiceField(queryset=Product.objects.all(), label='', required=True, widget=forms.Select(attrs={'id': 'participant-field'}))
