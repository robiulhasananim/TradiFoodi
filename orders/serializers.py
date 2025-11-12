from decimal import Decimal
from rest_framework import serializers
from .models import Order, OrderItem
from product.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'size', 'quantity', 'price', 'subtotal']
        read_only_fields = ['price', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'user', 'customer_name', 'contact_number',
            'delivery_address', 'delivery_note', 'total_amount',
            'payment_method', 'payment_status', 'payment_number', 'transaction_id',
            'status', 'created_at', 'items'
        ]
        read_only_fields = ['order_id', 'total_amount', 'created_at', 'user']

    def validate(self, attrs):
        """
        Ensure frontend total_amount matches backend calculation
        """
        items_data = attrs.get('items', [])
        backend_total = 0
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            backend_total += product.price * quantity

        frontend_total = attrs.get('total_amount', None)
        if frontend_total is not None and Decimal(frontend_total) != backend_total:
            raise serializers.ValidationError({
                "total_amount": f"Total amount mismatch! Backend: {backend_total}, Frontend: {frontend_total}"
            })
        # Set backend total_amount anyway
        attrs['total_amount'] = backend_total
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
            if not validated_data.get('customer_name'):
                validated_data['customer_name'] = request.user.get_full_name() or request.user.username

        order = Order.objects.create(**validated_data)

        # Create OrderItems
        for item_data in items_data:
            product = item_data['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                size=item_data.get('size'),
                quantity=item_data['quantity'],
                price=product.price
            )

        return order
