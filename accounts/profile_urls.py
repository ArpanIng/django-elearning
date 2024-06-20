from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/info/", views.ProfileEditView.as_view(), name="profile_update"),
    path("profile/photo/", views.ProfilePhotoEditView.as_view(), name="profile_photo_update"),
]
