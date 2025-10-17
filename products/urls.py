from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListView,
    ProductDetailView,
    ProductUpdateDeleteView
)

urlpatterns = [
    # Category
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # Product
    path('products/', ProductListView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', ProductUpdateDeleteView.as_view(), name='product-update-delete'),
]
