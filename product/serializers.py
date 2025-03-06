from rest_framework import serializers
from .models import Product, RTShip

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

    