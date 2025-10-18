from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'name', 
        'price', 
        'stock', 
        'sold', 
        'category', 
        'seller', 
        'status', 
        'thumbnail_preview', 
        'formatted_sizes',
        'created_at'
    )
    list_filter = ('status', 'category', 'seller', 'created_at')
    search_fields = ('name', 'description', 'color')
    readonly_fields = ('sold', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    autocomplete_fields = ('category', 'seller')
    list_per_page = 20

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'seller', 'status')
        }),
        ('Inventory & Price', {
            'fields': ('price', 'stock', 'sold')
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

    def display_sizes(self, obj):
        return ', '.join(obj.sizes or [])
    display_sizes.short_description = 'Available Sizes'

    def formatted_sizes(self, obj):
        """Display array of sizes in readable format."""
        if obj.sizes:
            return ", ".join(obj.sizes)
        return "—"
    formatted_sizes.short_description = 'Sizes'
