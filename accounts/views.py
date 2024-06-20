from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView

from carts.models import Cart
from carts.views import merge_carts
from courses.models import Course

from .forms import (
    CustomAuthenticationForm,
    ProfileForm,
    ProfilePhotoForm,
    RegistrationForm,
)


class RegistrationView(FormView):
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/auth/register.html"

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        messages.success(self.request, "Account created sucessfully!")
        return super(RegistrationView, self).form_valid(form)


class CustomLoginView(auth_views.LoginView):
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    template_name = "accounts/auth/login.html"

    def form_invalid(self, form):
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()
        anonymous_cart = None
        if not self.request.user.is_authenticated:
            session_key = self.request.session.session_key
            if session_key:
                try:
                    anonymous_cart = Cart.objects.get(session_key=session_key)
                except Cart.DoesNotExist:
                    pass

        login(self.request, user)

        if anonymous_cart:
            authenticated_cart, created = Cart.objects.get_or_create(user=user)
            merge_carts(anonymous_cart, authenticated_cart)
            anonymous_cart.delete()

        return super().form_valid(form)


class CustomLogoutView(auth_views.LogoutView):
    pass


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy("accounts:password_change_done")
    template_name = "accounts/auth/password_change_form.html"


class CustomPasswordChangeDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/auth/password_change_done.html"


class CustomPasswordResetView(auth_views.PasswordResetView):
    email_template_name = "accounts/auth/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    template_name = "accounts/auth/password_reset_form.html"


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/auth/password_reset_done.html"


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy("accounts:password_reset_complete")
    template_name = "accounts/auth/password_reset_confirm.html"


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/auth/password_reset_complete.html"


class ProfileView(LoginRequiredMixin, DetailView):
    """
    Display the profile details of the logged-in user.
    """

    model = get_user_model()
    context_object_name = "profile"
    template_name = "accounts/profile.html"

    def get_object(self):
        """
        Returns the currently logged-in user as the object for the view.
        """
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    View to edit the profile details of the logged-in user.
    """

    model = get_user_model()
    context_object_name = "profile"
    form_class = ProfileForm
    success_url = reverse_lazy("users:profile_update")
    template_name = "accounts/profile_form.html"

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = "profile_edit_page"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class ProfilePhotoEditView(LoginRequiredMixin, UpdateView):
    """
    View to edit the profile photo of the logged-in user.
    """

    model = get_user_model()
    context_object_name = "profile"
    form_class = ProfilePhotoForm
    success_url = reverse_lazy("users:profile_photo_update")
    template_name = "accounts/profile_photo.html"

    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = "profile_photo_page"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Profile photo updated successfully.")
        return super().form_valid(form)


class DashboardView(ListView):
    """
    Display a dashboard of courses for a request user.
    Courses are displayed regardless of its status.
    """

    model = Course
    context_object_name = "courses"
    template_name = "accounts/dashboard.html"

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user).order_by("-publish")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses_count = self.get_queryset().aggregate(total_courses=Count("id"))["total_courses"]
        context["courses_count"] = courses_count
        return context