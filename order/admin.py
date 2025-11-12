from django.contrib import admin
from django.db import transaction
from .models import Order, OrderItem, Product

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('order_id', 'customer_name', 'total_amount', 'payment_status', 'status')

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
