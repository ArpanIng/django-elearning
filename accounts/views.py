from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import CustomAuthenticationForm, RegistrationForm

User = get_user_model()


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
