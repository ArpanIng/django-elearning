import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError, transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from orders.models import Order, OrderItem

from .forms import CheckoutForm


class CheckoutView(LoginRequiredMixin, FormView):
    """Display and process the checkout process."""

    template_name = "orders/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("orders:order_completed")

    def get_cart_totals(self):
        """Calculate and return the cart totals."""
        # access cart from context-processor
        cart = self.request.cart
        return cart.calculate_total()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        (
            total_price,
            total_regular_price,
            total_discount_price,
            total_discount_percentage,
        ) = self.get_cart_totals()
        context["subtotal"] = total_regular_price
        context["total_discount"] = total_discount_price
        context["total"] = total_price
        return context

    def form_valid(self, form):
        user = self.request.user
        cart = self.request.cart

        (
            total_price,
            total_regular_price,
            total_discount_price,
            total_discount_percentage,
        ) = self.get_cart_totals()

        try:
            with transaction.atomic():  # ensures all query are executed as a single transaction
                # Save the order with the calculated totals
                order = form.save(commit=False)
                order.user = user
                order.subtotal = total_regular_price
                order.discount = total_discount_price
                order.total_amount = total_price
                order.save()

                # Create order items
                for course in cart.get_courses():
                    OrderItem.objects.create(
                        order=order,
                        course=course,
                        price=course.get_current_price(),
                    )
                # Clear the cart
                cart.items.all().delete()

                # Determine the selected payment method
                payment_method = form.cleaned_data["payment_method"]
                if payment_method == Order.PaymentOptions.KHALTI:
                    return redirect(
                        reverse("orders:khalti_payment", kwargs={"order_id": order.id})
                    )

        except DatabaseError:
            # Handle any errors that occur during the transaction
            messages.error(
                self.request,
                "There was an error processing your order. Please try again.",
            )
            return redirect("carts:cart")

        return super().form_valid(form)


class KhaltiPaymentView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        context = {"order": order}
        return render(request, "orders/khalti_payment.html", context)


@login_required
@require_POST
def initiate_khalti_payment(request):
    user = request.user
    # Khalti API endpoint for payment initiation
    url = "https://a.khalti.com/api/v2/epayment/initiate/"

    # Required fields
    return_url = request.POST.get("return_url")
    amount = request.POST.get("amount")
    purchase_order_id = request.POST.get("purchase_order_id")
    khalti_live_secret_key = settings.KHALTI_LIVE_SECRET_KEY

    exchange_rate = 132.0
    # convert the string amount into float
    float_khalti_amount = float(amount)
    # convert into float amount into Nepalese Rupee (npr)
    # 1 rupee = 100 paisa
    convert_to_npr = float_khalti_amount * exchange_rate
    # convert the float amount into integer
    # now the converted amount is considered 'paisa' for khalti payment
    khalti_amount = int(convert_to_npr)

    payload = json.dumps(
        {
            "return_url": return_url,
            "website_url": "http://127.0.0.1:8000/",
            "amount": khalti_amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "test",
            "customer_info": {
                "name": user.get_full_name(),
                "email": user.email,
            },
        }
    )
    headers = {
        "Authorization": f"key {khalti_live_secret_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except requests.RequestException:
        return HttpResponse("Failed to initiate Khalti payment.", status=500)

    if response.status_code == 200:
        payment_url = response.json()["payment_url"]
        if payment_url:
            # redirect to the khalti payment page
            return redirect(payment_url)
        else:
            return HttpResponse("Failed to retrieve Khalti payment URL.", status=500)
    else:
        return HttpResponse("Failed to initiate Khalti payment.")


@login_required
def verify_khalti_payment(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == "GET":
        pidx = request.GET.get("pidx")
        khalti_live_secret_key = settings.KHALTI_LIVE_SECRET_KEY

        payload = json.dumps(
            {
                "pidx": pidx,
            }
        )
        headers = {
            "Authorization": f"key {khalti_live_secret_key}",
            "Content-Type": "application/json",
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        new_response = json.loads(response.text)
        if new_response["status "] == "Completed":
            pass
        else:
            return redirect("/")


class OrderCompletedView(LoginRequiredMixin, TemplateView):
    template_name = "orders/order_completed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # user = user
        # id = id
        # order = get_object_or_404(Order, id=id, user=user)
        # context["order"] = order
        return context


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    context_object_name = "orders"
    template_name = "orders/order_list.html"

    def get_queryset(self):
        queryset = (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__course")
            .order_by("-ordered_date")
        )
        return queryset


class OrderSummaryView(DetailView):
    model = Order
    context_object_name = "order"
    template_name = "orders/order_summary.html"
