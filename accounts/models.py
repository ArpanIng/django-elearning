import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError("Email field is required.")

        if not username:
            raise ValueError("Username field is required.")

        if not first_name:
            raise ValueError("Firstname field is required.")

        if not last_name:
            raise ValueError("Lastname field is required.")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        # Save the user before adding groups
        user.save(using=self._db)

        # Determine the appropriate group based on the type of user being created
        if isinstance(user, Student):
            group_name = "Student"
        elif isinstance(user, Instructor):
            group_name = "Instructor"
        else:
            group_name = "Admin"

        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)  # Add user to their respective group

        # Set is_staff to True for Admin users
        if group_name == "Admin":
            user.is_staff = True
            user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None):
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for the application.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile = models.ImageField(
        default="default_user_profile.jpg",
        upload_to="User Profiles/",
        null=True,
        blank=True,
    )
    headline = models.CharField(
        max_length=80,
        help_text="Add a professional headline like, 'Instructor at Udemy' or 'Architect.'",
        null=True,
        blank=True,
    )
    about = models.TextField(null=True, blank=True)

    # social media links
    website_link = models.URLField(null=True, blank=True, help_text="Input your Website URL.")
    twitter_url = models.URLField(blank=True, null=True, help_text="Input your Twitter profile URL.")
    facebook_url = models.URLField(blank=True, null=True, help_text=" Input your Facebook profile URL.")
    linkedin_url = models.URLField(blank=True, null=True, help_text="Input your LinkedIn profile URL.")
    youtube_url = models.URLField(blank=True, null=True, help_text="Input your Youtube profile URL.")

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text="Designates that this user has all permissions without explicitly assigning them.",
    )

    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        if self.is_superuser:
            return True  # Superusers have all permissions
        else:
            # Delegate permission check to PermissionsMixin to handle permissions for non-superusers
            return super().has_perm(perm, obj)


class StudentManager(BaseUserManager):
    """Manager for the Student proxy model."""

    def get_queryset(self):
        return super().get_queryset().filter(groups__name="Student")


class Student(CustomUser):
    """Proxy model for users with the role of Student."""

    class Meta:
        proxy = True

    students = StudentManager()


class InstructorManager(BaseUserManager):
    """Manager for the Instructor proxy model."""

    def get_queryset(self):
        return super().get_queryset().filter(groups__name="Instructor")


class Instructor(CustomUser):
    """Proxy model for users with the role of Instructor."""

    class Meta:
        proxy = True

    instructors = InstructorManager()
