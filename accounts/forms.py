from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required fields, plus a repeated password.
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ["email", "username"]

    def clean_password2(self):
        """Check that the two password entries match"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        """Save the provided password in hashed format"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "password",
            "username",
            "is_active",
            "is_staff",
            "is_superuser",
        ]


class CustomAuthenticationForm(AuthenticationForm):
    """
    A custom authentication form to log in users with their email address.
    This form extends Django's built-in AuthenticationForm to use the
    email field for authentication instead of the default username field.
    """

    username = forms.CharField(
        label=get_user_model().USERNAME_FIELD.capitalize(),
        widget=forms.TextInput(attrs={"autofocus": True}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter email"},
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter password"},
        )


class RegistrationForm(UserCreationForm):
    """
    A Django ModelForm for user registration.
    """

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")  # sets the label_suffix to none
        super(RegistrationForm, self).__init__(*args, **kwargs)
        attrs = {"class": "form-control"}
        placeholders = {
            "first_name": "Enter First Name",
            "last_name": "Enter Last Name",
            "username": "Enter Username",
            "email": "Enter Email",
            "password1": "Enter Password",
            "password2": "Confirm Password",
        }
        for field_name, field in self.fields.items():
            field.widget.attrs.update(attrs)
            if field_name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[field_name]
