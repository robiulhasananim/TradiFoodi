# views.py
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework import status as drf_status
from .models import Order
from .serializers import OrderSerializer
from utils.helpers import Response  

# ---------- USER / GUEST VIEWS ----------

class OrderListCreateView(generics.ListCreateAPIView):
    """
    - Authenticated users can list their own orders
    - Guests can create orders
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'payment_status': ['exact'],
        'total_amount': ['exact', 'gte', 'lte'],
        'created_at': ['gte', 'lte'],
        'delivery_city': ['exact'],
    }
    search_fields = ['customer_name', 'customer_email', 'contact_number', 'delivery_city']
    ordering_fields = ['total_amount', 'created_at', 'delivery_city', 'order_id']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter().order_by('-created_at')
        return Order.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, message="Orders retrieved successfully")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data=serializer.data, message="Order created successfully", status=drf_status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


# ---------- SINGLE ORDER RETRIEVE & UPDATE ----------

class OrderDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Retrieve a single order and allow admin/staff to update
    only status or payment_status.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(data=serializer.data, message="Order retrieved successfully")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Allow PATCH only
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(data=serializer.data, message="Order updated successfully")
