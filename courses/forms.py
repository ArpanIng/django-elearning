from django import forms

from .models import Category, Course, CourseReview


class CourseForm(forms.ModelForm):
    """A form for creating and updating Course instances."""

    class Meta:
        model = Course
        fields = "__all__"
        exclude = ["slug", "instructor"]

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        # queryset for the 'category' field to include only parent categories.
        self.fields["category"].queryset = Category.objects.filter(parent=None)
        # queryset for the 'subcategory' field to include only non-parent categories.
        self.fields["subcategory"].queryset = Category.objects.filter(
            parent__isnull=False
        )


class CourseReviewForm(forms.ModelForm):
    class Meta:
        model = CourseReview
        # fields = "__all__"
        fields = ["rating", "content"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs.update(
            {
                "placeholder": "Tell us about you own personal experience taking this course. Was it a good match for you?",
                "rows": 6,
            }
        )
