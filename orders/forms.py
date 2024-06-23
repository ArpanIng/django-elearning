from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=Order.PaymentOptions.choices, widget=forms.RadioSelect
    )

    class Meta:
        model = Order
        fields = ["country", "payment_method"]
