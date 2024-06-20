from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget

from .forms import UserChangeForm, UserCreationForm
from .models import CustomUser


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ["email", "username", "last_login", "is_staff"]
    list_display_links = ["email", "username"]
    list_filter = [
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    ]
    fieldsets = [
        (None, {"fields": ["id", "email", "password"]}),
        (
            "Personal info",
            {
                "fields": [
                    "username",
                    "first_name",
                    "last_name",
                    "profile",
                    "headline",
                    "about",
                ]
            },
        ),
        (
            "Social links",
            {
                "fields": [
                    "website_link",
                    "twitter_url",
                    "facebook_url",
                    "linkedin_url",
                    "youtube_url",
                ]
            },
        ),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ]
            },
        ),
        ("Important dates", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "username", "password1", "password2"],
            },
        ),
    ]
    readonly_fields = ["id", "last_login", "date_joined"]
    search_fields = ["email", "username"]
    ordering = ["email"]
    filter_horizontal = ["groups", "user_permissions"]
    # Configure formfield_overrides to apply CKEditor5Widget for about field
    formfield_overrides = {
        models.TextField: {
            "widget": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="custom_config"
            )
        },
    }


admin.site.register(CustomUser, UserAdmin)
