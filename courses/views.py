from django.shortcuts import render

def index(request):
    return render(request, "courses/index.html")

def about_view(request):
    return render(request, "about.html")

def contact_view(request):
    return render(request, "contact_us.html")

def course_list(request):
    return render(request, "courses/course_list.html")

def course_detail(request):
    return render(request, "courses/course_detail.html")