from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, PAYMENT_METHOD_CHOICES
from product.models import Product
from drf_spectacular.utils import extend_schema_field


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='product_id',
        source='product'
    )
    product_name = serializers.ReadOnlyField(source='product.name')
    subtotal = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'item_id',
            'product_id',
            'product_name',
            'size',
            'color',
            'quantity',
            'price',
            'subtotal',
        ]
        extra_kwargs = {
            'price': {'read_only': True},
        }
        read_only_fields = ['item_id']
    
    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_subtotal(self, obj):
        return obj.subtotal()


class CustomerProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20, required=False)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    totalPrice = serializers.DecimalField(source='total_amount', max_digits=12, decimal_places=2, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    # Accept profile info in the payload
    profile = CustomerProfileSerializer(write_only=True)
    
    # Read-only profile fields fetched via relations for output
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.ReadOnlyField(source='user.email')
    contact_number = serializers.SerializerMethodField()
    deliveryAddress = serializers.SerializerMethodField()
    deliveryCity = serializers.SerializerMethodField()
    deliveryPostalCode = serializers.SerializerMethodField()
    
    paymentMethod = serializers.CharField(source='payment_method')

    class Meta:
        model = Order
        fields = [
            'order_id',
            'user',
            'profile',  # Included for input
            'customer_name',
            'customer_email',
            'contact_number',
            'deliveryAddress',
            'deliveryCity',
            'deliveryPostalCode',
            'delivery_note',
            'paymentMethod',
            'totalPrice',
            'status',
            'items',
            'created_at',
        ]
        read_only_fields = ['order_id', 'created_at', 'totalPrice', 'customer_name', 'customer_email', 'contact_number', 'deliveryAddress', 'deliveryCity', 'deliveryPostalCode']

    def get_customer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_contact_number(self, obj):
        return obj.user.phone

    def get_deliveryAddress(self, obj):
        return obj.user.address

    def get_deliveryCity(self, obj):
        return obj.user.city

    def get_deliveryPostalCode(self, obj):
        return obj.user.postal_code

    def validate_paymentMethod(self, value):
        if value.lower() != 'cod':
            raise serializers.ValidationError("Only 'COD' (Cash on Delivery) is supported for now.")
        return value.lower()

    def validate(self, data):
        if not self.instance:  # Only on create
            if not data.get('items'):
                raise serializers.ValidationError({"items": "At least one item is required."})
            if not data.get('profile'):
                raise serializers.ValidationError({"profile": "Profile information is required to place an order."})
            
            # Additional check: If email is being changed, ensure it's not taken by another user
            request = self.context.get('request')
            new_email = data.get('profile', {}).get('email')
            if new_email and request.user.email != new_email:
                from account.models import User
                if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                    raise serializers.ValidationError({"profile": {"email": "This email is already taken by another account."}})
                    
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        items_data = validated_data.pop('items', [])
        profile_data = validated_data.pop('profile', {})

        # Update user profile information
        user.first_name = profile_data.get('first_name', user.first_name)
        user.last_name = profile_data.get('last_name', user.last_name)
        user.email = profile_data.get('email', user.email)
        user.phone = profile_data.get('phone', user.phone)
        user.address = profile_data.get('address', user.address)
        user.city = profile_data.get('city', user.city)
        user.postal_code = profile_data.get('postal_code', user.postal_code)
        user.save()

        order = Order.objects.create(
            user=user,
            **validated_data
        )

        total = Decimal('0.00')

        for item_data in items_data:
            product = item_data.get('product')
            quantity = item_data.get('quantity')

            # Fetch product with row-level lock
            product = Product.objects.select_for_update().get(pk=product.id)

            if quantity <= 0:
                raise serializers.ValidationError("Quantity must be greater than 0.")
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. Available: {product.stock}"
                )

            price = product.price
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

        order.total_amount = total.quantize(Decimal('0.01'))
        order.save()

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
