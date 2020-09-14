from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal'),
)


class CheckoutForm(forms.Form):
    # name = forms.CharField(required=True)
    # mobile = forms.CharField(required=True)
    pin_code = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'pin code',
        'class': 'form-control'
    }))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    # city = forms.CharField(required=True)
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'class': 'form-control'
    }))
    # state = forms.CharField(required=True)
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100'
        }))
    # same_shipping_address = forms.BooleanField(
    #     required=False, widget=forms.CheckboxInput())
    # save_address = forms.BooleanField(
    #     required=False, widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)
