from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'city', 'status', 'payment_method', 'payment_completed', 'created', 'updated']
    list_filter = ['status', 'payment_method', 'payment_completed', 'created', 'updated']
    search_fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'external_id']
    date_hierarchy = 'created'
    readonly_fields = ['created', 'updated']
    inlines = [OrderItemInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']
    extra = 0


class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created', 'updated']
    inlines = [CartItemInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)
