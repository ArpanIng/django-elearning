from django import forms

from .models import Category, Course


class CourseForm(forms.ModelForm):
    """A form for creating and updating Course instances."""
    class Meta:
        model = Course
        fields = "__all__"
        exclude= ["slug", "instructor"]
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        # queryset for the 'category' field to include only parent categories.
        self.fields["category"].queryset = Category.objects.filter(parent=None)
        # queryset for the 'subcategory' field to include only non-parent categories.
        self.fields["subcategory"].queryset = Category.objects.filter(parent__isnull=False)