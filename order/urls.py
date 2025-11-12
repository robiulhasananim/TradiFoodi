# urls.py
from django.urls import path
from .views import OrderListCreateView, OrderDetailUpdateAPIView

urlpatterns = [
    # List all orders for the authenticated user or create a new order
    path('', OrderListCreateView.as_view(), name='order-list-create'),

    # Retrieve a single order by ID and update its status/payment_status
    path('<int:pk>/', OrderDetailUpdateAPIView.as_view(), name='order-detail-update'),
]
