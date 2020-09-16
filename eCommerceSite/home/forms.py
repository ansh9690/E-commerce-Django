from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'Paypal'),
)

STATE_CHOICES = (
    ('', "Select state"),
    ("AP", "Andhra Pradesh"),
    ("AR", "Arunachal Pradesh"),
    ("AS", "Assam"),
    ("BR", "Bihar"),
    ("CT", "Chhattisgarh"),
    ("CH", "Chandigarh"),
    ("DN", "Dadra and Nagar Haveli"),
    ("DD", "Daman and Diu"),
    ("DL", "Delhi"),
    ("GA", "Goa"),
    ("GJ", "Gujarat"),
    ("HR", "Haryana"),
    ("HP", "Himachal Pradesh"),
    ("JK", "Jammu and Kashmir"),
    ("JH", "Jharkhand"),
    ("KA", "Karnataka"),
    ("KL", "Kerala"),
    ("MP", "Madhya Pradesh"),
    ("MH", "Maharashtra"),
    ("MN", "Manipur"),
    ("ML", "Meghalaya"),
    ("MZ", "Mizoram"),
    ("NL", "Nagaland"),
    ("OR", "Orissa"),
    ("PB", "Punjab"),
    ("PY", "Pondicherry"),
    ("RJ", "Rajasthan"),
    ("SK", "Sikkim"),
    ("TN", "Tamil Nadu"),
    ("TR", "Tripura"),
    ("UP", "Uttar Pradesh"),
    ("UK", "Uttarakhand"),
    ("WB", "West Bengal")
)


class CheckoutForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'full name',
        'class': 'form-control'
    }))
    mobile = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': '10 digits mubile number',
        'class': 'form-control'
    }))
    pin_code = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'pin code',
        'class': 'form-control'
    }))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'class': 'form-control'
    }))
    state = forms.CharField(
        widget=forms.Select(choices=STATE_CHOICES, attrs={
            'class': 'form-control'
        }),

    )
    # country = CountryField(blank_label='(select country)').formfield(
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100'
    #     }))
    # same_shipping_address = forms.BooleanField(
    #     required=False, widget=forms.CheckboxInput())
    # save_address = forms.BooleanField(
    #     required=False, widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
    }))


class RequestFrom(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'cols': '100',
        'rows': '5'
    }))
    email = forms.EmailField()
