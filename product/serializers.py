from rest_framework import serializers
from .models import *
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
        extra_kwargs = {
            'slug': {'required': False}  # Make slug not required in serializer
        }

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
    
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'
class CollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionList
        fields = '__all__'
 
class CartItemSerializer(serializers.ModelSerializer):
    product=ProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity','total']
    def get_total(self, cart_item):
        total = cart_item.product.price * cart_item.quantity
        return total
class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(read_only=True, many=True)
    num_of_items = serializers.SerializerMethodField()
    sum_of_items = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'cart_code','sum_of_items','num_of_items','items', 'created_at', 'modified_at']
    def get_num_of_items(self, cart):
        num_of_items = sum([item.quantity for item in cart.items.all()])
        return num_of_items
    def get_sum_of_items(self, cart):
        sum_of_items = sum([item.product.price * item.quantity for item in cart.items.all()])
        return sum_of_items
    
class SimpleCartSerializer(serializers.ModelSerializer):
    number_of_items = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields =['id','cart_code','number_of_items']

    def get_number_of_items(self, cart):
        number_of_items =sum ([item.quantity for item in cart.items.all()])
        return number_of_items