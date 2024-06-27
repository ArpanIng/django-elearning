from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# Custom error handler view page
handler403 = "courses.error_handlers.handler403"
handler404 = "courses.error_handlers.handler404"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", include("courses.urls", namespace="courses")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("user/", include("accounts.profile_urls", namespace="profiles")),
    path("cart/", include("carts.urls", namespace="carts")),
    path("", include("orders.urls", namespace="orders")),
]

if settings.DEBUG:
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
