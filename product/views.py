from rest_framework import generics, filters
from .models import *
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework.permissions import AllowAny
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view

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
        collection_key = self.request.query_params.get('collection')  # Slug key like 'collection1'

        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)

        if collection_key:
            queryset = queryset.filter(collection=collection_key)

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

class Collection(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCollectionSerializer
 
@api_view(['POST'])
def add_item(request):
    try:
        cart_code = request.data.get('cart_code')
        product_id = request.data.get('product_id')

        cart, created = Cart.objects.get_or_create(cart_code=cart_code)
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity =1
        cart_item.save()
    except Exception as e:
        return Response({'message': str(e)}, status=400)

    serializer = CartItemSerializer(cart_item)
    return Response({'data': serializer.data, 'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def product_in_cart(request):
    cart_code = request.query_params.get('cart_code')
    product_id = request.query_params.get('product_id')
    if not cart_code or not product_id:
        return Response({'error': 'cart_code and product_id are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cart = Cart.objects.get(cart_code=cart_code)
        product = Product.objects.get(id=product_id)
        product_exists_in_cart = CartItem.objects.filter(cart=cart, product=product).exists()
        return Response({'product_in_cart': product_exists_in_cart})
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_cart_status(request):
    cart_code = request.query_params.get('cart_code')
    logger.debug(f'Received cart_code: {cart_code}')
    if not cart_code:
        return Response({'error': 'cart_code is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cart = Cart.objects.get(cart_code=cart_code, paid=False)    
        serializer = SimpleCartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f'Error retrieving cart status: {e}')
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def get_cart(request):
    cart_code = request.query_params.get('cart_code')
    cart= Cart.objects.get(cart_code=cart_code)
    serrializer = CartSerializer(cart)
    return Response(serrializer.data)


@api_view(['patch'])
def update_quantity(request):
    try:
        cartitem_id = request.data.get('item_id')
        quantity =int(request.data.get('quantity'))
        cartitem = CartItem.objects.get(id=cartitem_id)
        cartitem.quantity = quantity
        cartitem.save()
        serializer = CartItemSerializer(cartitem)
        return Response({'data': serializer.data, 'message': 'Cart item updated sucessfully!'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_cartitem(request):
    cartitem_id = request.data.get('item_id')
    cartitem = CartItem.objects.get(id=cartitem_id)
    cartitem.delete()
    return Response({'message': 'Cart item deleted sucessfully!'}, status=status.HTTP_204_NO_CONTENT)