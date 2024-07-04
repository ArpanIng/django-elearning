from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    # Filter out the 'Free Coupon' option
    payment_method_choices = [
        (choice.value, choice.label)
        for choice in Order.PaymentOptions
        if choice.value != Order.PaymentOptions.FREE.value
    ]

    payment_method = forms.ChoiceField(
        choices=payment_method_choices, widget=forms.RadioSelect
    )

    class Meta:
        model = Order
        fields = ["country", "payment_method"]
