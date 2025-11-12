import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from product.models import Product

User = settings.AUTH_USER_MODEL

PAYMENT_METHOD_CHOICES = (
    ('bkash', 'bKash'),
    ('rocket', 'Rocket'),
    ('nagad', 'Nagad'),
    ('cod', 'Cash on Delivery'),
)

PAYMENT_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
)

ORDER_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_id = models.CharField(max_length=15, unique=True, editable=False)
    
    # Guest & user both
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=20)
    delivery_address = models.TextField()
    delivery_note = models.TextField(blank=True, null=True)

    # manual payment handel
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_number = models.CharField(max_length=30, blank=True, null=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = 'ORD-' + uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)

    def calculate_total(self):
        #Efficient total calculation method (called manually)
        total = sum(item.subtotal() for item in self.items.all())
        self.total_amount = total
        return total

    def __str__(self):
        return f"{self.order_id} - {self.customer_name or self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)  # price at the time of order (per unit)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"
