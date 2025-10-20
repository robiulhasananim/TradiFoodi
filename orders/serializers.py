from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product

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

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
            if not validated_data.get('customer_name'):
                validated_data['customer_name'] = request.user.get_full_name() or request.user.username
