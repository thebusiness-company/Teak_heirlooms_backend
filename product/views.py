from rest_framework import generics
from .models import *
from rest_framework.permissions import AllowAny
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

class CategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'slug'

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    parser_classes = (MultiPartParser, FormParser)

class SubCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    lookup_field = 'slug'
    parser_classes = (MultiPartParser, FormParser)

class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    queryset = Product.objects.prefetch_related('images').all()
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = super().get_queryset()
        subcategory_slug = self.request.query_params.get('subcategory')
        
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
            
        return queryset

    def perform_create(self, serializer):
        product = serializer.save()
        images = self.request.FILES.getlist("images")
        for image in images:
            ProductImage.objects.create(product=product, image=image)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    lookup_field = "slug"
    parser_classes = (MultiPartParser, FormParser)

    def perform_update(self, serializer):
        product = serializer.save()
        if "images" in self.request.FILES:
            product.images.all().delete()
            for image in self.request.FILES.getlist("images"):
                ProductImage.objects.create(product=product, image=image)

class SubCategoryByCategoryView(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    
    def get_queryset(self):
        category_name = self.request.query_params.get('category')
        if category_name:
            return SubCategory.objects.filter(
                category__name__iexact=category_name
            )
        return SubCategory.objects.none()
    

class RTShipPagination(PageNumberPagination):
    page_size = 10  # Number of products per page
    page_size_query_param = 'page_size'  # Allows clients to request custom page sizes
    max_page_size = 100  # Optional limit

class RTShipListView(generics.ListCreateAPIView):
    queryset = RTShip.objects.all().order_by('-id')
    serializer_class = RTShipSerializer
    pagination_class = RTShipPagination

# class Collection(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductCollectionSerializer