from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'subtotal')

    def subtotal(self, obj):
        return obj.subtotal()
    subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'user', 'total_amount', 'payment_status', 'status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_id', 'customer_name', 'contact_number', 'transaction_id')
    readonly_fields = ('order_id', 'total_amount', 'created_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
