from rest_framework import generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Review
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from .filters import ProductFilter
from django.utils.text import slugify
from account.permission import IsAdmin,IsSeller,IsAdminOrSeller,ReadOnlyOrAdmin,ReadOnlyOrAdminOrSeller
from utils.helpers import Response
from utils.swagger_helpers import wrapped_response_serializer
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg, Count


# ---------------- Category Views ----------------

@extend_schema_view(
    get=extend_schema(
        summary="List Categories (Public)",
        description="Retrieve all categories.",
        request=None,
        responses=wrapped_response_serializer(CategorySerializer, many=True)
    ),
    post=extend_schema(
        summary="Create Category (Admin/Seller)",
        description="Create a new category. Only Admins or Sellers can create.",
        request=CategorySerializer,
        responses=wrapped_response_serializer(CategorySerializer)
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
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
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
                message="Category creation failed.",
                status=status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors
            )

@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Category (Public)",
        description="Get details of a specific category.",
        request=None,
        responses=wrapped_response_serializer(CategorySerializer)
    ),
    put=extend_schema(
        summary="Update Category (Admin/Seller)",
        description="Update a category's details. Only Admins or Sellers can update.",
        request=CategorySerializer,
        responses=wrapped_response_serializer(CategorySerializer)
    ),
    patch=extend_schema(
        summary="Partial Update Category (Admin/Seller)",
        description="Partial update of a category's details.",
        request=CategorySerializer,
        responses=wrapped_response_serializer(CategorySerializer)
    ),
    delete=extend_schema(
        summary="Delete Category (Admin/Seller)",
        description="Delete a category. Only Admins or Sellers can delete.",
        request=None,
        responses=wrapped_response_serializer()
    )
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdminOrSeller]
    lookup_field = 'cat_id'
    lookup_url_kwarg = 'cat_id'

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
        summary="List Products (Public)",
        description="Retrieve all products with filtering, search, and sorting.",
        request=None,
        responses=wrapped_response_serializer(ProductSerializer, many=True)
    ),
    post=extend_schema(
        summary="Create Product (Admin/Seller)",
        description="Create a new product. Only Admins or Sellers can create.",
        request=ProductSerializer,
        responses=wrapped_response_serializer(ProductSerializer)
    )
)
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.annotate(
        rating_avg=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAdminOrSeller]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'rating_avg', 'created_at', 'name']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            status=status.HTTP_200_OK,
            message="Product list fetched successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                success=True,
                message="Product created successfully.",
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            success=False,
            message="Product creation failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )
    
@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Product (Public)",
        description="Get details of a specific product.",
        request=None,
        responses=wrapped_response_serializer(ProductSerializer)
    ),
    put=extend_schema(
        summary="Update Product (Admin/Seller)",
        description="Update a product. Only the seller who owns the product or Admin can update.",
        request=ProductSerializer,
        responses=wrapped_response_serializer(ProductSerializer)
    ),
    patch=extend_schema(
        summary="Partial Update Product (Admin/Seller)",
        description="Partial update of a product.",
        request=ProductSerializer,
        responses=wrapped_response_serializer(ProductSerializer)
    ),
    delete=extend_schema(
        summary="Delete Product (Admin/Seller)",
        description="Delete a product. Only the seller who owns the product or Admin can delete.",
        request=None,
        responses=wrapped_response_serializer()
    )
)
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.annotate(
        rating_avg=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAdminOrSeller]
    lookup_field = 'product_id'
    lookup_url_kwarg = 'product_id'

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
        if request.user != instance.seller and not (request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)):
            return Response(success=False, message="Permission denied.", status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(
                success=True,
                message="Product updated successfully.",
                data=serializer.data
            )
        return Response(
            success=False,
            message="Product update failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user != instance.seller and not (request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)):
            return Response(success=False, message="Permission denied.", status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(
            success=True,
            message="Product deleted successfully.",
            data=None,
            status=status.HTTP_200_OK
        )

# ---------------- Review Views ----------------

@extend_schema_view(
    get=extend_schema(
        summary="List Reviews (Public)",
        description="Retrieve all reviews for a specific product.",
        responses=wrapped_response_serializer(ReviewSerializer, many=True)
    ),
    post=extend_schema(
        summary="Post Review (Authenticated)",
        description="Post a review for a specific product. Authenticated users only.",
        request=ReviewSerializer,
        responses=wrapped_response_serializer(ReviewSerializer)
    )
)
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product__product_id=self.kwargs['product_id'])

    def perform_create(self, serializer):
        product = Product.objects.get(product_id=self.kwargs['product_id'])
        if Review.objects.filter(product=product, user=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You have already reviewed this product.")
        serializer.save(user=self.request.user, product=product)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success=True,
            status=status.HTTP_200_OK,
            message="Reviews fetched successfully.",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
            except Exception as e:
                return Response(
                    success=False,
                    message=str(e),
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                success=True,
                message="Review posted successfully.",
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            success=False,
            message="Review posting failed.",
            status=status.HTTP_400_BAD_REQUEST,
            errors=serializer.errors
        )
