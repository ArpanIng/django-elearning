from django.shortcuts import render

def handler403(request, exception):
    return render(request, "errors/403.html", status=403)

def handler404(request, exception):
    return render(request, "errors/404.html", status=404)