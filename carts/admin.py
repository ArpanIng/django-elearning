from django.contrib import admin

from .models import Cart, CartItem

admin.site.register(Cart)


@admin.register(CartItem)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ["cart", "course", "date_added"]
    readonly_fields = ["date_added"]
    
