from rest_framework import generics
from .models import Product, RTShip
from .serializers import ProductSerializer, RTShipSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = "slug"

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
class RTShipPagination(PageNumberPagination):
    page_size = 10  # Number of products per page
    page_size_query_param = 'page_size'  # Allows clients to request custom page sizes
    max_page_size = 100  # Optional limit

class RTShipListView(generics.ListCreateAPIView):
    queryset = RTShip.objects.all().order_by('-id')
    serializer_class = RTShipSerializer
    pagination_class = RTShipPagination