from django import forms
from django.contrib import admin

from .models import (
    Category,
    Course,
    CourseRequirement,
    Enrollment,
    Lesson,
    Module,
    WhatYoullLearn,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "parent")
    prepopulated_fields = {"slug": ("title",)}


class ParentCategoryChoiceField(forms.ModelChoiceField):
    """
    Custom form field for parent categories
    """

    def __init__(self, *args, **kwargs):
        kwargs["queryset"] = Category.objects.filter(parent=None)
        super().__init__(*args, **kwargs)


class SubCategoryChoiceField(forms.ModelChoiceField):
    """
    Custom form field for subcategories
    """

    def __init__(self, *args, **kwargs):
        kwargs["queryset"] = Category.objects.filter(parent__isnull=False)
        super().__init__(*args, **kwargs)


class CourseAdminForm(forms.ModelForm):
    """
    CourseAdmin to use CourseAdminForm and customize list_display
    """

    category = ParentCategoryChoiceField()
    subcategory = SubCategoryChoiceField(required=False)

    class Meta:
        model = Course
        fields = "__all__"


class ParentCategoryFilter(admin.SimpleListFilter):
    """
    Custom filter to display and filter course by parent category.
    """

    title = "Category"
    parameter_name = "category"

    def lookups(self, request, model_admin):
        """Returns a list of tuples representing the filter options."""
        return Category.objects.filter(parent=None).values_list("slug", "title")

    def queryset(self, request, queryset):
        """Filters the queryset based on the selected filter option."""
        if self.value():
            return queryset.filter(category__slug=self.value())


class SubCategoryFilter(admin.SimpleListFilter):
    """
    Custom filter to display and filter courses by subcategory.
    """

    title = "Subcategory"
    parameter_name = "subcategory"

    def lookups(self, request, model_admin):
        """Returns a list of tuples representing the filter options."""
        return Category.objects.filter(parent__isnull=False).values_list(
            "slug", "title"
        )

    def queryset(self, request, queryset):
        """Filters the queryset based on the selected filter option."""
        if self.value():
            return queryset.filter(subcategory__slug=self.value())


class CourseRequirementInline(admin.StackedInline):
    model = CourseRequirement


class CourseWhatYoullLearnInline(admin.StackedInline):
    model = WhatYoullLearn


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = [
        "title",
        "instructor",
        "regular_price",
        "discount_price",
        "publish",
        "updated",
        "status",
    ]
    list_filter = [
        "status",
        "publish",
        "level",
        "is_free",
        ParentCategoryFilter,
        SubCategoryFilter,
    ]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    # raw_id_fields = ["instructor"]
    date_hierarchy = "publish"
    ordering = ["status", "-publish"]
    inlines = [CourseRequirementInline, CourseWhatYoullLearnInline, ModuleInline]


class LessonInline(admin.StackedInline):
    model = Lesson


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "course"]
    inlines = [LessonInline]


@admin.register(Lesson)
class LessionAdmin(admin.ModelAdmin):
    list_display = ["title"]


admin.site.register(Enrollment)
