from rest_framework import serializers
from .models import Product, RTShip, Room, Collection, CollectionList,Category, SubCategory, ProductImage
# serializers.py
from rest_framework import serializers
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', 
        queryset=Category.objects.all(),
        required=True
    )
    
    class Meta:
        model = SubCategory
        fields = "__all__"
        

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.SlugRelatedField(
        slug_field='slug', 
        queryset=Category.objects.all(),
        required=True
    )
    subcategory = serializers.SlugRelatedField(
        slug_field='slug', 
        queryset=SubCategory.objects.all(), 
        required=False, 
        allow_null=True
    )
    
    class Meta:
        model = Product
        fields = "__all__"
        
    
    def validate_dimensions(self, value):
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("Dimensions must be a valid JSON object")
        return value
    
    def validate_finishes(self, value):
        if value and not isinstance(value, list):
            raise serializers.ValidationError("Finishes must be a valid JSON array")
        return value

class RTProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['name', 'slug', 'price', 'images','in_stock']

class RTShipSerializer(serializers.ModelSerializer):
    product=RTProductSerializer()
    class Meta:
        model = RTShip
        fields = ['product', 'NewArrival', 'MostSold']

class ProductCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['slug','category']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
    
# class CollectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Collection
#         fields = '__all__'
# class CollectionListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CollectionList
#         fields = '__all__'