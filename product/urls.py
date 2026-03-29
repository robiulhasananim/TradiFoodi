from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    ReviewListCreateView
)

urlpatterns = [
    # Category
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<str:cat_id>/', CategoryDetailView.as_view(), name='category-detail'),

    # Product
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<str:product_id>/', ProductDetailView.as_view(), name='product-detail'),

    # Reviews
    path('<str:product_id>/reviews/', ReviewListCreateView.as_view(), name='product-reviews'),
]