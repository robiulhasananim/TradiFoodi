from rest_framework import serializers
from .models import Product, Category
from django.utils.text import slugify

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug']
        read_only_fields = ['slug']

        def create(self, validated_data):
            if 'slug' not in validated_data or not validated_data['slug']:
                validated_data['slug'] = slugify(validated_data.get('name'))
            return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            validated_data['slug'] = slugify(validated_data.get('name'))
        return super().update(instance, validated_data)

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)  
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'sold', 'category',
            'seller','thumbnail','images','sizes' 'color', 'status', 'created_at', 'updated_at'
        ]
    
    read_only_fields = ['sold','seller', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Automatically set the seller 
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['seller'] = request.user
        return super().create(validated_data)