from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListView,
    ProductDetailView
)

urlpatterns = [
    # Category
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # Product
    path('', ProductListView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
