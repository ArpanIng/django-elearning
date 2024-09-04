from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Avg
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

from accounts.models import Instructor


class Category(models.Model):
    """
    Model representing a category and its subcategories.
    Note:
        - To create a top-level category, do not specify the parent.
        - To create a subcategory, provide the parent category to which it belongs.
    """

    title = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="children",
    )
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

    def get_category_url(self):
        """return the URL of the category itself."""
        return reverse(
            "courses:courses_by_category", kwargs={"category_slug": self.slug}
        )

    def get_subcategory_url(self):
        """return the URL of the category and subcategory."""
        return reverse(
            "courses:courses_by_subcategory",
            kwargs={"category_slug": self.parent.slug, "subcategory_slug": self.slug},
        )

    @staticmethod
    def get_categories():
        """Retrieve top-level categories with their subcategories prefetched."""
        return Category.objects.filter(parent__isnull=True).prefetch_related("children")


class PublishedManager(models.Manager):
    """
    Custom Manager
    Returns: Course with 'PUBLISHED' status
    """

    def get_queryset(self):
        return super().get_queryset().filter(status=Course.Status.PUBLISHED)


class Course(models.Model):
    """Model representing a course."""

    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    class DifficultyLevel(models.TextChoices):
        ALL_LEVELS = "ALL", "All Levels"
        BEGINNER = "BE", "Beginner"
        INTERMEDIATE = "IN", "Intermediate"
        ADVANCED = "AD", "Advanced"

    class PriceStatus(models.TextChoices):
        FREE = "FREE", "Free"
        PAID = "PAID", "Paid"

    title = models.CharField(max_length=250, help_text="Enter course title.")
    slug = models.SlugField(max_length=250, unique=True)
    summary = models.CharField(max_length=800, help_text="Enter a summary of a course.")
    description = CKEditor5Field("Description", config_name="extends")
    regular_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Price of the course.",
    )
    discount_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="Discount price of the course.",
    )
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PUBLISHED,
        help_text="Select the status of the course.",
    )
    featured_image = models.ImageField(
        default="default_course_image.jpg", upload_to="Courses/", null=True
    )
    price_status = models.CharField(
        max_length=4,
        choices=PriceStatus.choices,
        default=PriceStatus.PAID,
        help_text="Indicates whether the course is available for free or not.",
    )
    certificate = models.BooleanField(
        default=False,
        help_text="Indicates whether the course provides a certificate upon completion.",
    )
    level = models.CharField(
        max_length=4, choices=DifficultyLevel.choices, default=DifficultyLevel.BEGINNER
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        help_text="Assign parent category",
        related_name="parent_courses",
    )
    subcategory = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        help_text="Assign sub category",
        related_name="subcategory_courses",
        null=True,
        blank=True,
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name="courses",
    )
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Enrollment")
    publish = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = models.Manager()  # default Manager
    published = PublishedManager()  # custom published Manager

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["publish"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"course_slug": self.slug})

    def get_enroll_url(self):
        return reverse("courses:course_enroll", kwargs={"course_slug": self.slug})

    def get_unenroll_url(self):
        return reverse("courses:course_unenroll", kwargs={"course_slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("carts:add_to_cart", kwargs={"course_slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("carts:remove_from_cart", kwargs={"course_slug": self.slug})

    def is_free(self):
        return self.price_status == Course.PriceStatus.FREE

    def has_discount(self):
        """helps determine whether a course has a discount or not"""
        return self.discount_price > 0.00 and self.discount_price < self.regular_price

    def get_current_price(self):
        return self.discount_price if self.has_discount() else self.regular_price

    def get_reviews(self):
        return self.reviews.all().prefetch_related("user")

    def get_reviews_count(self):
        return self.reviews.all().count()

    def get_total_enrolled_students_count(self):
        return self.students.count()

    def get_average_ratings(self):
        queryset = self.reviews.all()
        return queryset.aggregate(average_rating=Avg("rating"))["average_rating"]

    @property
    def get_discount_percentage(self):
        if self.has_discount():
            discount_price = self.regular_price - self.discount_price
            discount_percentage = round((discount_price / self.regular_price) * 100)
            return discount_percentage
        return 0  # Return 0 when the regular_price is 0 to avoid division by zero error

    def clean(self):
        if self.price_status == self.PriceStatus.FREE:
            self.regular_price = 0.00
            self.discount_price = 0.00
        elif self.price_status == self.PriceStatus.PAID:
            if self.regular_price <= 0.00:
                raise ValidationError(
                    "Regular price must be set and greater than zero for paid courses."
                )
            if self.discount_price > self.regular_price:
                raise ValidationError(
                    "Discount price cannot be greater than the regular price."
                )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.full_clean()
        return super().save(*args, **kwargs)


class Module(models.Model):
    """Model representing a module within a course."""

    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Specify the order in which this module should appear in the course.",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
        help_text="Select the corresponding course to associate this module with.",
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Model representing a lesson within a module."""

    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(
        help_text="Specify the order in which this lesson should appear in the course."
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """Model representing the enrollment of a student in a course."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrolled",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrollment_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student}: {self.course.title}"


class CourseReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField(max_length=1000)
    reviewed_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} on course {self.course} Rating: {self.rating}"
