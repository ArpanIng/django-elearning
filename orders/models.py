import uuid

from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

from courses.models import Course


class Order(models.Model):
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
        help_text="Total regular price of courses in the cart before any discounts.",
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


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The final price of the course at the time of purchase.",
    )

    def __str__(self):
        return f"{self.course.title} in order {self.order.id}"


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    payment_method = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Current status of the payment.",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     # Assign payment method from the associated order
    #     self.payment_method = self.order.payment_method
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id}"
