from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("courses/", views.course_list, name="course_list"),
    path("course/detail/", views.course_detail, name="course_detail"),
]
