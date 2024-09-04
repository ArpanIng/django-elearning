import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField

from courses.models import Course


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"

    class PaymentOptions(models.TextChoices):
        STRIPE = "STP", "Stripe"
        ESEWA = "ES", "eSewa"
        KHALTI = "KH", "Khalti"
        FREE = "FC", "Free Coupon"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Ordered by"
    )
    country = CountryField()
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total regular price of courses before any discounts.",
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Discout amount applied.",
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Final amount to be paid."
    )
    order_status = models.CharField(
        max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    payment_method = models.CharField(max_length=10, choices=PaymentOptions.choices)
    courses = models.ManyToManyField(Course, through="OrderItem")
    is_completed = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["-ordered_date"]),
        ]

    def __str__(self):
        return f"Order ID: {self.id}"

    def get_absolute_url(self):
        return reverse("orders:order_completed", kwargs={"order_id": self.id})


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The final price of the course at the time of purchase.",
    )

    class Meta:
        unique_together = ("order", "course")

    def __str__(self):
        return f"{self.course.title} in order {self.order.id}"
