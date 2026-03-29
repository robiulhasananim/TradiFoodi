import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(method='filter_category')
    rating = django_filters.NumberFilter(field_name="rating_avg", lookup_expr='gte')
    isAvailable = django_filters.BooleanFilter(field_name="isAvailable")

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'rating', 'isAvailable']

    def filter_category(self, queryset, name, value):
        if value.isdigit():
            return queryset.filter(category__id=value)
        return queryset.filter(category__slug=value)
