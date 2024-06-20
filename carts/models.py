from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone

from courses.models import Course


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    courses = models.ManyToManyField(Course, through="CartItem")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ID: {self.id}"

    def add_course(self, course):
        """Add course to the cart."""
        cartitem, created = CartItem.objects.get_or_create(cart=self, course=course)
        return cartitem

    def remove_course(self, course):
        """Remove the course from the cart."""
        cartitem = get_object_or_404(CartItem, cart=self, course=course)
        if cartitem:
            cartitem.delete()

    def get_courses(self) -> list:
        """
        Retrieve a list of courses associated with the items in the cart, ordered by the added date.
        """

        # cart_items = self.items.prefetch_related('course').all().order_by("-date_added")
        cart_items = self.items.select_related("course").all().order_by("-date_added")
        courses = [item.course for item in cart_items]
        return courses

    def calculate_total_regular_price(self):
        """Calculate the total regular price of all courses in the cart."""
        return sum(course.regular_price for course in self.get_courses())

    def calculate_total_discount_price(self):
        """Calculate the total discount price of all discounted courses in the cart."""
        return sum(
            course.regular_price - course.discount_price
            for course in self.get_courses()
            if course.has_discount()
        )

    def calculate_total_price(self):
        """Calculate the total current price of all courses in the cart."""
        return sum(course.get_current_price() for course in self.get_courses())

    def calculate_total_discount_percentage(self):
        """Calculate the total discount percentage for all courses in the cart."""
        total_regular_price = self.calculate_total_regular_price()
        total_discount_price = self.calculate_total_discount_price()
        return (
            round((total_discount_price / total_regular_price) * 100)
            if total_regular_price > 0
            else 0
        )

    def calculate_total(self):
        total_price = self.calculate_total_price()
        total_regular_price = self.calculate_total_regular_price()
        total_discount_percentage = self.calculate_total_discount_percentage()
        return total_price, total_regular_price, total_discount_percentage


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.cart} CartItem: {self.id}"
