from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView

from courses.models import Course


def merge_carts(anonymous_cart, authenticated_cart):
    """
    Merge items from the anonymous cart into the authenticated cart.
    Args:
        anonymous_cart (Cart): The cart associated with the anonymous session.
        authenticated_cart (Cart): The cart associated with the authenticated user.
    """

    for item in anonymous_cart.items.all():
        # Check if the course already exists in the authenticated cart
        if not authenticated_cart.items.filter(course=item.course).exists():
            # If the course doesn't exist in the authenticated cart, add it
            item.cart = authenticated_cart
            item.save()


def add_to_cart(request, course_slug):
    course_obj = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        cart = request.cart
        # Add course to the cart
        cart.add_course(course=course_obj)
        return redirect("carts:cart")
    return redirect(course_obj.get_absolute_url())


def remove_from_cart(request, course_slug):
    course_obj = get_object_or_404(Course, slug=course_slug)
    if request.method == "POST":
        cart = request.cart
        # remove course from the cart
        cart.remove_course(course=course_obj)
        return redirect("carts:cart")
    return redirect(course_obj.get_absolute_url())


class CartView(TemplateView):
    template_name = "carts/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.cart
        context["cart"] = cart
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
        context["cart"] = cart
        return context
