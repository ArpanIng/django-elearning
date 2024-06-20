from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ["user", "session_key", "created_at", "updated_at"]
    list_display_links = ["user", "session_key"]
    readonly_fields = ["session_key"]


@admin.register(CartItem)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ["cart", "course", "date_added"]
    readonly_fields = ["date_added"]