from rest_framework import generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.utils.text import slugify
from accounts.permissions import IsAdmin,IsSeller,IsAdminOrSellerForWriteReadOnlyOtherwise
from utils.helpers import Response


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrSellerForWriteReadOnlyOtherwise]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        if 'slug' not in validated_data or not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data.get('name'))
        serializer.save()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Category list fetched successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            success=True,
            message="Category created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrSellerForWriteReadOnlyOtherwise]

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        if 'name' in validated_data:
            validated_data['slug'] = slugify(validated_data['name'])
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Category details retrieved.",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Category updated successfully.",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            success=True,
            message="Category deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK
        )

# Product Views
class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrSellerForWriteReadOnlyOtherwise]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__id', 'price', 'color', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sold', 'created_at']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Product list fetched successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            success=True,
            message="Product created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrSellerForWriteReadOnlyOtherwise]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Product details retrieved.",
            data=serializer.data
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # ensure seller owns this product
        if request.user != instance.seller and not request.user.is_admin:
            return Response(success=False, message="Permission denied.", status_code=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            success=True,
            message="Product updated successfully.",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user != instance.seller and not request.user.is_admin:
            return Response(success=False, message="Permission denied.", status_code=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(
            success=True,
            message="Product deleted successfully.",
            data=None,
            status_code=status.HTTP_200_OK
        )
