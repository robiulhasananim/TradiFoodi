from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, PAYMENT_METHOD_CHOICES
from product.models import Product
from drf_spectacular.utils import extend_schema_field


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual order items.
    Frontend may send product ID and quantity only.
    Price and subtotal are computed securely on the backend.
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'size',
            'color',
            'quantity',
            'price',
            'subtotal',
        ]
        extra_kwargs = {
            'price': {'read_only': True},  # backend sets price
        }
    
    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderSerializer(serializers.ModelSerializer):
    """
    Handles both user and guest orders securely.
    - Ignores frontend-submitted price/total
    - Validates stock and product existence
    - Calculates total_amount on the backend
    - Prevents sensitive data leaks for non-admin users
    """
    items = OrderItemSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'user',
            'customer_name',
            'customer_email',
            'contact_number',
            'delivery_address',
            'delivery_city',
            'delivery_note',
            'total_amount',
            'payment_method',
            'payment_status',
            'payment_number',
            'transaction_id',
            'status',
            'items',
            'created_at',
        ]
        read_only_fields = ['order_id', 'created_at', 'total_amount']

    extra_kwargs = {
        'customer_name': {'required': True},
        'payment_method': {'required': True}
    }

    # ---------- VALIDATION ----------

    def validate_payment_method(self, value):
        if value and value not in dict(PAYMENT_METHOD_CHOICES):
            raise serializers.ValidationError("Invalid payment method.")
        return value

    def validate(self, data):
        if not self.instance:  # Only on create
            if not data.get('contact_number'):
                raise serializers.ValidationError({"contact_number": "Contact number is required."})
            if not data.get('delivery_address'):
                raise serializers.ValidationError({"delivery_address": "Delivery address is required."})
            if not data.get('delivery_city'):
                raise serializers.ValidationError({"delivery_city": "Delivery city is required."})
            if not data.get('items'):
                raise serializers.ValidationError({"items": "At least one item is required."})
        return data


    # ---------- CREATE ORDER ----------

    @transaction.atomic
    def create(self, validated_data):
        """
        Securely create an order (guest or user):
        - Ignores frontend prices
        - Validates stock
        - Deducts stock
        - Calculates total_amount
        """
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        items_data = validated_data.pop('items', [])

        # Create order (user or guest)
        order = Order.objects.create(**validated_data)

        total = Decimal('0.00')

        for item_data in items_data:
            product_id = item_data.get('product').id
            quantity = item_data.get('quantity')

            # Fetch product with row-level lock
            product = Product.objects.select_for_update().get(pk=product_id)

            if quantity <= 0:
                raise serializers.ValidationError("Quantity must be greater than 0.")
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.stock}, requested: {quantity}."
                )

            # Always use backend product price
            price = product.price

            # Deduct stock safely
            product.stock -= quantity
            product.sold += quantity
            product.save()

            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                size=item_data.get('size'),
                color=item_data.get('color'),
                quantity=quantity,
                price=price,
            )
            total += order_item.subtotal()

        # Set total
        order.total_amount = total.quantize(Decimal('0.01'))
        order.save()

        # Optional: Guest tracking
        if not user and request:
            ip = request.META.get('REMOTE_ADDR')
            # You can log guest order info in a separate model or analytics table
            print(f"Guest order created from IP: {ip}")

        return order

    # ---------- UPDATE ORDER ----------

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Securely update order status (admin/staff only).
        If order is cancelled, restore stock for all items.
        """
        user = self.context['request'].user if 'request' in self.context else None

        # --- Permission check: only staff or role='admin' can update ---
        if not user or (not user.is_staff and getattr(user, 'role', None) != 'admin'):
            raise serializers.ValidationError("You don't have permission to modify this order.")
        
        # Prevent changing cancelled orders
        if instance.status == 'cancelled':
            raise serializers.ValidationError("This order has been cancelled and cannot be modified.")

        # --- Only allow status update ---
        allowed_fields = ['status', 'payment_status']
        for key in validated_data.keys():
            if key not in allowed_fields:
                raise serializers.ValidationError("Only order status or payment status can be updated by admin.")

        new_status = validated_data.get('status', instance.status)
        new_payment_status = validated_data.get('payment_status', instance.payment_status)
        # --- Restore stock if order is cancelled ---
        if new_status == 'cancelled' and instance.status != 'cancelled':
            for item in instance.items.all():
                product = item.product
                if product:
                    product.stock += item.quantity
                    product.save()

        # --- Update the order status ---
        instance.status = new_status
        instance.payment_status = new_payment_status
        instance.save()

        return instance

    # ---------- REPRESENTATION ----------

    def to_representation(self, instance):
        """
        Hide sensitive payment data for non-admin users.
        """
        data = super().to_representation(instance)
        user = self.context['request'].user if 'request' in self.context else None

        # Hide payment info if user is not staff OR role != 'admin'
        if not user or (not user.is_staff and getattr(user, 'role', None) != 'admin'):
            data.pop('payment_number', None)
            data.pop('transaction_id', None)
            data.pop('payment_status', None)

        return data
