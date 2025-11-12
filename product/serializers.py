from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug']
        read_only_fields = ['slug']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    seller = serializers.StringRelatedField(read_only=True)  
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'sold', 'category', 'category_id',
            'seller','thumbnail','images','sizes', 'color', 'is_active', 'created_at', 'updated_at'
        ]
    
    read_only_fields = ['sold','seller', 'created_at', 'updated_at']
    extra_kwargs = {
        'name': {'required': True},
        'description': {'required': True},
        'price': {'required': True},
        'stock': {'required': True},
        'category_id': {'required': True},
    }

    # Validation Methods 
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def validate_images(self, value):
        max_images = 5
        if value and len(value) > max_images:
            raise serializers.ValidationError(f"Maximum {max_images} images allowed.")
        return value

    def validate_sizes(self, value):
        max_sizes = 5
        if value and len(value) > max_sizes:
            raise serializers.ValidationError(f"Maximum {max_sizes} sizes allowed.")
        return value

    def validate_color(self, value):
        max_colors = 5
        if value and len(value) > max_colors:
            raise serializers.ValidationError(f"Maximum {max_colors} colors allowed.")
        return value

    # Override create to assign seller automatically 
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['seller'] = request.user
        return super().create(validated_data)