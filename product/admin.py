from django.contrib import admin
from .models import Category, Product, Review
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('cat_id', 'name', 'slug', 'image', 'description')
    search_fields = ('cat_id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_id', 
        'name', 
        'price', 
        'stock', 
        'sold', 
        'category', 
        'seller', 
        'isAvailable', 
        'thumbnail_preview', 
        'formatted_sizes',
        'created_at'
    )
    list_filter = ('isAvailable', 'category', 'seller', 'created_at')
    search_fields = ('product_id', 'name', 'description', 'color')
    readonly_fields = ('sold', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('category', 'seller')
    list_per_page = 20

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'seller', 'isAvailable')
        }),
        ('Inventory & Price', {
            'fields': ('price', 'originalPrice', 'stock', 'sold')
        }),
        ('Details', {
            'fields': ('ingredients', 'preparationTime', 'servingSize')
        }),
        ('Visuals', {
            'fields': ('thumbnail', 'images', 'color', 'sizes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def thumbnail_preview(self, obj):
        """Display thumbnail preview in admin list."""
        if obj.thumbnail:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 6px;" />', obj.thumbnail)
        return "No Image"
    thumbnail_preview.short_description = 'Thumbnail'

    def formatted_sizes(self, obj):
        """Display array of sizes in readable format."""
        if obj.sizes:
            return ", ".join(obj.sizes)
        return "—"
    formatted_sizes.short_description = 'Sizes'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rating', 'comment', 'createdAt')
    list_filter = ('rating', 'createdAt')
    search_fields = ('comment', 'user__email', 'product__name')
    readonly_fields = ('createdAt',)
