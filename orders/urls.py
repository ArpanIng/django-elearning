from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("order/completed/", views.OrderCompletedView.as_view(), name="order_completed"),
    path("purchase-history/", views.OrderListView.as_view(), name="order_list"),
    path("order/summary/", views.OrderSummaryView.as_view(), name="order_detail"),
    path("payment/checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("payment/khalti/<uuid:order_id>/", views.KhaltiPaymentView.as_view(), name="khalti_payment"),
    path("khalti/initiate/", views.initiate_khalti_payment, name="khalti_initiate"),
    path("khalti/verify/", views.verify_khalti_payment, name="khalti_verify"),
]
