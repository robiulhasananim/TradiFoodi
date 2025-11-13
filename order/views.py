# views.py
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status as drf_status
from .models import Order
from .serializers import OrderSerializer
from utils.helpers import Response 
from drf_spectacular.utils import extend_schema,extend_schema_view
from utils.swagger_helpers import CustomResponseSerializer
from account.permission import ReadOnlyOrAdmin,IsAdminOrSeller

# ---------- USER / GUEST VIEWS ----------
@extend_schema_view(
    get=extend_schema(
        summary="List Orders (Authenticated users/admin/seller)",
        description="Admin or Seller can see all orders, regular users see only their own. Guests cannot list orders.",
        responses=CustomResponseSerializer
    ),
    post=extend_schema(
        summary="Create Order (Guest or Authenticated User)",
        description="Anyone can create an order, no authentication required.",
        request=OrderSerializer,
        responses=CustomResponseSerializer
    )
)
class OrderListCreateView(generics.ListCreateAPIView):
    """
    - Admin/Seller: Can list all orders
    - Authenticated user: Can list only their own orders
    - Guests: Can create orders, cannot list orders
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
            if getattr(user, 'role', None) in ['admin', 'seller']:
                return Order.objects.all().order_by('-created_at')
            return Order.objects.filter(user=user).order_by('-created_at')
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
@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Single Order (Authenticated users/admin/seller)",
        description="Admin/Seller can retrieve any order, regular users can retrieve only their own order.",
        responses=CustomResponseSerializer
    ),
    patch=extend_schema(
        summary="Update Order and Payment Status (Admin/Seller Only)",
        description="Only Admin or Seller can update `status` or `payment_status`. Regular users cannot update.",
        request=OrderSerializer,
        responses=CustomResponseSerializer
    )
)
class OrderDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    - Admin/Seller: Can retrieve any order and update only `status` or `payment_status`
    - Regular user: Can retrieve only their own order
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrSeller]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) in ['admin', 'seller'] or user.is_staff:
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
