from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "country",
        "subtotal",
        "discount",
        "total_amount",
        "ordered_date",
    ]
    ordering = ["-ordered_date"]
    list_filter = ["payment_method", "is_completed"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = ["order", "course", "price"]
