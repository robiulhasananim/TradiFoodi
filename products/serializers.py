from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug']
        read_only_fields = ['slug']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = serializers.StringRelatedField(read_only=True)  
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'sold', 'category',
            'seller','thumbnail','images','sizes', 'color', 'status', 'created_at', 'updated_at'
        ]
    
    read_only_fields = ['sold','seller', 'created_at', 'updated_at']
