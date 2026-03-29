from rest_framework import serializers
from .models import Product, Category, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['cat_id', 'name', 'slug', 'image', 'description']
        read_only_fields = ['cat_id', 'slug']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ['review_id', 'user', 'rating', 'comment', 'createdAt']
        read_only_fields = ['review_id', 'user', 'createdAt']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='cat_id',
        source='category',
        write_only=True
    )
    seller = serializers.StringRelatedField(read_only=True)
    rating = serializers.FloatField(source='rating_avg', read_only=True, default=0)
    reviewCount = serializers.IntegerField(source='review_count', read_only=True, default=0)

    class Meta:
        model = Product
        fields = [
            'product_id', 'name', 'description', 'price', 'originalPrice', 'stock', 'sold', 
            'category', 'category_id', 'seller', 'thumbnail', 'images', 
            'ingredients', 'preparationTime', 'servingSize',
            'sizes', 'color', 'isAvailable', 'rating', 'reviewCount', 'created_at', 'updated_at'
        ]
    
    read_only_fields = ['product_id', 'sold','seller', 'created_at', 'updated_at', 'rating', 'reviewCount']
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