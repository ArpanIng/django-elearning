from django.contrib import admin

from .models import Order, OrderItem, Payment


admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
# class OrderModelAdmin(admin.ModelAdmin):
#     list_display = ["id", "user", "subtotal", "discount", "total_amount", "ordered_date"]
#     ordering = ["-ordered_date"]


# @admin.register(OrderItem)
# class OrderItemModelAdmin(admin.ModelAdmin):
#     list_display = ["order", "course", "price"]