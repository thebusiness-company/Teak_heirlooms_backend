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
from rest_framework import filters 
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
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        subcategory_slug = self.request.query_params.get('subcategory')
        collection_key = self.request.query_params.get('collection')

        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)

        if collection_key:
            # FIX: Check if the key is a number before filtering by ID
            if collection_key.isdigit():
                # If it's a number (e.g., "1"), check both ID and Custom ID
                queryset = queryset.filter(
                    Q(collection__id=collection_key) | 
                    Q(collection__custom_id=collection_key)
                )
            else:
                # If it's a string (e.g., "title3"), ONLY check Custom ID
                queryset = queryset.filter(collection__custom_id=collection_key)


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
        finishes = request.data.get('finishes')
        quantity = request.data.get('quantity',1)


        cart, created = Cart.objects.get_or_create(cart_code=cart_code)
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.finishes = finishes
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

from .models import ShopCollection
from .serializers import ShopCollectionSerializer

class ShopCollectionAPIView(APIView):
    """
    API View to retrieve list of Shop Collections
    """
    def get(self, request, *args, **kwargs):
        try:
            collections = ShopCollection.objects.all()
            # context={'request': request} is crucial for generating full image URLs
            serializer = ShopCollectionSerializer(collections, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Something went wrong fetching collections"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def post(self,request,*args, **kwargs):
        try:
            serializer = ShopCollectionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "something went wrong creating collection"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ShopCollectionDetailView(APIView):

    parser_classes = (MultiPartParser, FormParser)


    def get_object(self,pk):
            
        try:
            if pk.isdigit():
                return ShopCollection.objects.filter(
                    Q(id=pk) | Q(custom_id=pk)
                ).first()
            else:
                return ShopCollection.objects.get(custom_id=pk)
        except ShopCollection.DoesNotExist:
            return None
        

    def get(self, request, pk, *args,**kwargs):
        collection = self.get_object(pk)
        if collection is None:
            return Response({"error":"Collection not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShopCollectionSerializer(collection, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, pk,*args,**kwargs):
        collection =self.get_object(pk)
        if collection is None:
            return Response({"error":"collection not found"},status= status.HTTP_404_NOT_FOUND)
        serializer = ShopCollectionSerializer(collection, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request,pk,*args,**kwargs):
        collection =self.get_object(pk)
        if collection is None:
            return Response({"error":"Collection not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer=ShopCollectionSerializer(collection, data=request.data, partial=True, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request,pk,*args,**kwargs):
        collection =self.get_object(pk)
        if collection is None:
            return Response({"error":"Collection not found"},status=status.HTTP_404_NOT_FOUND)
        collection.delete()
        return Response({"message":"Collection deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    

    