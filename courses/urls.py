from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("contact/", views.ContactUsView.as_view(), name="contact"),
    path("about/", views.AboutView.as_view(), name="about"),
]

urlpatterns += [
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path("courses/search/", views.CourseListView.as_view(), name="search"),
    path(
        "courses/<slug:category_slug>/",
        views.CourseListView.as_view(),
        name="courses_by_category",
    ),
    path(
        "courses/<slug:category_slug>/<slug:subcategory_slug>/",
        views.CourseListView.as_view(),
        name="courses_by_subcategory",
    ),
]

urlpatterns += [
    path("course/create/", views.CourseCreateView.as_view(), name="course_create"),
    path("course/<slug:course_slug>/", views.CourseDetailView.as_view(), name="course_detail"),
    path("course/<slug:course_slug>/edit/", views.CourseEditView.as_view(), name="course_edit"),
    path("course/<slug:course_slug>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),
]
