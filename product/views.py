from rest_framework import generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django.utils.text import slugify
from account.permission import IsAdmin,IsSeller,IsAdminOrSeller,ReadOnlyOrAdmin,ReadOnlyOrAdminOrSeller
from utils.helpers import Response
from utils.swagger_helpers import CustomResponseSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema


# ---------------- Category Views ----------------

@extend_schema_view(
    get=extend_schema(
        summary="List Categories (ReadOnly/Admin/Seller)",
        description="Retrieve all categories. Admins and sellers can see all, read-only users can view only.",
        request=None,
        responses=CustomResponseSerializer
    ),
    post=extend_schema(
        summary="Create Category (Admin/Seller)",
        description="Create a new category. Only Admins or Sellers can create.",
        request=CategorySerializer,
        responses=CustomResponseSerializer
    )
)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminOrSeller]
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
            status=status.HTTP_200_OK,
            message="Category list fetched successfully.",
            data=serializer.data
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                success=True,
                message="Category created successfully.",
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
                success=False,
                message="Category created Faild.",
                status=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Category (ReadOnly/Admin/Seller)",
        description="Get details of a specific category.",
        request=None,
        responses=CustomResponseSerializer
    ),
    put=extend_schema(
        summary="Update Category (Admin/Seller)",
        description="Update a category's details. Only Admins or Sellers can update.",
        request=CategorySerializer,
        responses=CustomResponseSerializer
    ),
    patch=extend_schema(
        summary="Partial Update Category (Admin/Seller)",
        description="Partial update of a category's details.",
        request=CategorySerializer,
        responses=CustomResponseSerializer
    ),
    delete=extend_schema(
        summary="Delete Category (Admin/Seller)",
        description="Delete a category. Only Admins or Sellers can delete.",
        request=None,
        responses=CustomResponseSerializer
    )
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminOrSeller]

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
            status=status.HTTP_200_OK,
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
            status=status.HTTP_200_OK,
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
            status=status.HTTP_200_OK
        )

# ---------------- Product Views ----------------

@extend_schema_view(
    get=extend_schema(
        summary="List Products (ReadOnly/Admin/Seller)",
        description="Retrieve all products. Users with read-only access can view only.",
        request=None,
        responses=CustomResponseSerializer
    ),
    post=extend_schema(
        summary="Create Product (Admin/Seller)",
        description="Create a new product. Only Admins or Sellers can create.",
        request=ProductSerializer,
        responses=CustomResponseSerializer
    )
)
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAdminOrSeller]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
    'category__id': ['exact'],
    'price': ['exact', 'gte', 'lte'],
    'created_at': ['gte', 'lte'],
    'is_active': ['exact'],
    }
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'sold', 'created_at']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            status=status.HTTP_200_OK,
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
            status=status.HTTP_201_CREATED
        )
    
@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Product (ReadOnly/Admin/Seller)",
        description="Get details of a specific product.",
        request=None,
        responses=CustomResponseSerializer
    ),
    put=extend_schema(
        summary="Update Product (Admin/Seller)",
        description="Update a product. Only the seller who owns the product or Admin can update.",
        request=ProductSerializer,
        responses=CustomResponseSerializer
    ),
    patch=extend_schema(
        summary="Partial Update Product (Admin/Seller)",
        description="Partial update of a product.",
        request=ProductSerializer,
        responses=CustomResponseSerializer
    ),
    delete=extend_schema(
        summary="Delete Product (Admin/Seller)",
        description="Delete a product. Only the seller who owns the product or Admin can delete.",
        request=None,
        responses=CustomResponseSerializer
    )
)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.filter()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAdminOrSeller]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            success=True,
            status=status.HTTP_200_OK,
            message="Product details retrieved.",
            data=serializer.data
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # ensure seller owns this product
        if request.user != instance.seller and not request.user.is_admin:
            return Response(success=False, message="Permission denied.", status=status.HTTP_403_FORBIDDEN)

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
            return Response(success=False, message="Permission denied.", status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(
            success=True,
            message="Product deleted successfully.",
            data=None,
            status=status.HTTP_200_OK
        )
