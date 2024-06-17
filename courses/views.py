from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import CourseForm
from .models import Category, Course

User = get_user_model()


class IndexView(TemplateView):
    template_name = "courses/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # fetches all published courses (6 records) with their associated instructors
        published_courses = Course.published.select_related("instructor").all()[:6]
        context["courses"] = published_courses
        return context


class CourseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Course
    form_class = CourseForm
    success_message = "Course created successfully!"
    template_name = "courses/course_form.html"

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        response = super().form_valid(form)
        if self.object.status == Course.Status.DRAFT:
            return redirect("accounts:dasboard")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context    


class CourseListView(ListView):
    """
    Displays a list of courses filtered by either search params, category or subcategory.
    """

    model = Course
    context_object_name = "courses"
    template_name = "courses/course_list.html"

    def get_queryset(self):
        queryset = Course.published.all().select_related("instructor")
        query = self.request.GET.get("q")
        category = self.kwargs.get("category_slug")
        subcategory = self.kwargs.get("subcategory_slug")

        # filter course based on search params
        if query:
            lookups = Q(title__icontains=query) | Q(description__icontains=query)
            queryset = queryset.filter(lookups)

        # filter course based on category or subcategory
        if category:
            queryset = queryset.filter(category__slug=category)

        if subcategory:
            queryset = queryset.filter(subcategory__slug=subcategory)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        category_slug = self.kwargs.get("category_slug")
        subcategory_slug = self.kwargs.get("subcategory_slug")
        # for breadcrumb navigation
        # filters the current url category and it's childrens
        category = Category.objects.filter(slug=category_slug, parent__isnull=True).prefetch_related("children")
        # count courses accordingly to the returned queryset (by search, category, and subcategory)
        courses_count = self.get_queryset().aggregate(count=Count("id"))

        # based on the slug, access the title
        if category_slug:
            category_slug = Category.objects.get(slug=category_slug)
            context["title"] = category_slug.title
        if subcategory_slug:
            subcategory_slug = Category.objects.get(slug=subcategory_slug)
            context["title"] = subcategory_slug.title

        context["category"] = category
        context["query"] = query
        context["subcategory"] = subcategory_slug
        context["results_count"] = courses_count["count"]
        return context


class CourseDetailView(DetailView):
    model = Course
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "course_slug"
    template_name = "courses/course_detail.html"

    def get_queryset(self):
        return Course.published.all()


class CourseEditView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = Course
    form_class = CourseForm
    slug_field = "slug"
    slug_url_kwarg = "course_slug"
    success_message = "Course details updated successfully."
    template_name = "courses/course_form.html"

    def test_func(self):
        course = self.get_object()
        return course.instructor == self.request.user
    
    def get_success_url(self):
        course = self.get_object()
        if course.status == Course.Status.DRAFT:
            return reverse("accounts:dashboard")
        else:
            return course.get_absolute_url()


class CourseDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView
):
    model = Course
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "course_slug"
    success_message = "The course has been deleted successfully."
    success_url = reverse_lazy("accounts:dashboard")
    template_name = "courses/course_delete.html"

    def test_func(self):
        course = self.get_object()
        return course.instructor == self.request.user


class AboutView(TemplateView):
    template_name = "about.html"


class ContactUsView(TemplateView):
    template_name = "contact_us.html"
