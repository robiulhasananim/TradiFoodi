from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock', 'sold', 'category', 'seller', 'status', 'created_at')
    list_filter = ('status', 'category', 'seller', 'created_at')
    search_fields = ('name', 'description', 'color')
    readonly_fields = ('sold', 'created_at', 'updated_at')
    ordering = ('-created_at',)
