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

    def calculate_total(self) -> tuple[float]:
        """
        Calculate the total price of all courses, including regular price, discount price,
        and the total discount percentage.
        Returns:
            tuple: A tuple containing:
            - total_price (float): The total price after applying discounts.
            - total_regular_price (float): The sum of regular prices of all courses.
            - total_discount_percentage (float): The percentage of the discount applied,
              rounded to the nearest whole number. If there are no courses or the total
              regular price is zero, this will be 0.
        """

        total_price = 0
        total_regular_price = 0
        total_discount_price = 0
        total_discount_percentage = 0

        for course in self.get_courses():
            if course.has_discount():
                total_price += course.discount_price
                total_discount_price = course.regular_price - course.discount_price
            else:
                total_price += course.regular_price

            total_regular_price += course.regular_price

        if total_regular_price > 0:
            total_discount_percentage = round((total_discount_price / total_regular_price) * 100)

        return total_price, total_regular_price, total_discount_price, total_discount_percentage


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.cart} CartItem: {self.id}"
