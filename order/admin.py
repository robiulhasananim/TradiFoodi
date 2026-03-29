from django.contrib import admin
from django.db import transaction
from .models import Order, OrderItem, Product

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = (
        'order_id', 
        'get_customer_name', 
        'get_contact_number', 
        'get_delivery_city', 
        'total_amount', 
        'payment_status', 
        'status', 
        'created_at'
    )
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_id', 'user__email', 'user__first_name', 'user__last_name', 'user__phone')
    readonly_fields = (
        'order_id', 
        'total_amount', 
        'get_customer_name', 
        'get_contact_number', 
        'get_delivery_address', 
        'get_delivery_city', 
        'get_delivery_postal_code',
        'created_at'
    )

    fieldsets = (
        ('Order ID', {'fields': ('order_id', 'created_at')}),
        ('Customer Info', {'fields': ('get_customer_name', 'get_contact_number')}),
        ('Shipping Info', {'fields': ('get_delivery_address', 'get_delivery_city', 'get_delivery_postal_code', 'delivery_note')}),
        ('Payment Info', {'fields': ('total_amount', 'payment_method', 'payment_status', 'payment_number', 'transaction_id')}),
        ('Status', {'fields': ('status',)}),
    )

    def get_customer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_customer_name.short_description = 'Customer Name'

    def get_contact_number(self, obj):
        return obj.user.phone
    get_contact_number.short_description = 'Contact Number'

    def get_delivery_address(self, obj):
        return obj.user.address
    get_delivery_address.short_description = 'Delivery Address'

    def get_delivery_city(self, obj):
        return obj.user.city
    get_delivery_city.short_description = 'Delivery City'

    def get_delivery_postal_code(self, obj):
        return obj.user.postal_code
    get_delivery_postal_code.short_description = 'Postal Code'

    def save_formset(self, request, form, formset, change):
        """This is called for inline OrderItems"""
        with transaction.atomic():
            instances = formset.save(commit=False)
            for item in instances:
                # Check stock
                if item.product and item.quantity:
                    if item.product.stock < item.quantity:
                        raise ValueError(f"Not enough stock for {item.product.name}")

                    # Deduct stock
                    item.product.stock -= item.quantity
                    item.product.save()

                item.save()
            formset.save_m2m()

            # After all items saved, update total_amount
            order = form.instance
            order.total_amount = sum(item.subtotal() for item in order.items.all())
            order.save()
