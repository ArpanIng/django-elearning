from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView

from courses.models import Course

from .models import Cart

CART_SESSION_KEY = "cart_id"


def add_to_cart(request, course_slug):
    course_obj = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        # check if cart exists
        cart_id = request.session.get(CART_SESSION_KEY, None)

        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()
            # assign the created cart id to the cart session
            request.session[CART_SESSION_KEY] = cart.id

        # Add course to the cart
        cart.add_course(course=course_obj)
        return redirect("carts:cart")
    return redirect(course_obj.get_absolute_url())


def remove_from_cart(request, course_slug):
    course_obj = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        # check if cart exists
        cart_id = request.session.get(CART_SESSION_KEY, None)
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id)
            cart.remove_course(course=course_obj)
        return redirect("carts:cart")
    return redirect(course_obj.get_absolute_url())


class CartView(TemplateView):
    template_name = "carts/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get(CART_SESSION_KEY)

        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id)
            courses = cart.get_courses()

            # tuple unpacking / assigns each value to its corresponding variable
            total_price, total_regular_price, total_discount_percentage = (
                cart.calculate_total()
            )
            context["courses"] = courses
            context["courses_count"] = len(courses)
            context["total_price"] = total_price
            context["total_regular_price"] = total_regular_price
            context["total_discount_percentage"] = total_discount_percentage
        else:
            cart = None

        context["cart"] = cart
        return context


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "carts/checkout.html"


class OrderCompletedView(LoginRequiredMixin, TemplateView):
    template_name = "carts/order_completed.html"
