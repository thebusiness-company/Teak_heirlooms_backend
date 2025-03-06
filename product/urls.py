from django.urls import path
from .views import ProductListCreateView, ProductDetailView, RTShipListView

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('RTShip/', RTShipListView.as_view(), name='product-detail'),
    
]
