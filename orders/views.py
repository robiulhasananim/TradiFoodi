from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Order
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework import status

# -----------------------------
# List Orders (GET)
# -----------------------------
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(user=user).order_by('-created_at')
        return Order.objects.none()  # Guests can't see orders

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "status_code": 200,
            "message": "Order list fetched successfully",
            "data": serializer.data
        })


# -----------------------------
# Create Order (POST)
# -----------------------------
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({
            "success": True,
            "status_code": 201,
            "message": "Order placed successfully",
            "data": self.get_serializer(order).data
        }, status=status.HTTP_201_CREATED)


# -----------------------------
# Order Detail (GET)
# -----------------------------
class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]  # Adjust if only user can see their orders
