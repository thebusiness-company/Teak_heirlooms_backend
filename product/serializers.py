from rest_framework import serializers
from .models import Product, RTShip, Room, Collection, CollectionList

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class RTProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'price', 'image','in_stock']

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