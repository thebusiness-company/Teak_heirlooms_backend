from django.urls import path
from .views import *

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('subcategories/', SubCategoryListCreateView.as_view(), name='subcategory-list'),
    path('subcategories/<slug:slug>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),
    path('subcategories/by-category/', SubCategoryByCategoryView.as_view(), name='subcategories-by-category'),
    path('RTShip/', RTShipListView.as_view(), name='product-detail'),
    path('collection/', Collection.as_view(), name='collection'),
    path('add_item/', add_item, name='add_item'),
    path('product_in_cart/', product_in_cart, name='product_in_cart'),
    path('get_cart_status', get_cart_status, name='get_cart_status'),
    path('get_cart/',get_cart, name='get_cart'),
    path('update_quantity/',update_quantity, name='update_quantity'),
    path('delete_cartitem/',delete_cartitem, name='delete_cartitem'),
    
]
