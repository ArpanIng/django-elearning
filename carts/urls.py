from django.urls import path

from . import views

app_name = "carts"

urlpatterns = [
    path("", views.CartView.as_view(), name="cart"),
    path("add/<slug:course_slug>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<slug:course_slug>/", views.remove_from_cart, name="remove_from_cart"),
]