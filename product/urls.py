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
    # path('collection/', Collection.as_view(), name='collection'),
    
]
