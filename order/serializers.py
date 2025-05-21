from rest_framework import serializers
from .models import  Order, OrderAddress
from product.serializers import CartSerializer
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = '__all__'
        
class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer()
    address = AddressSerializer()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'cart',
            'razorpay_order_id',
            'razorpay_payment_id',
            'payment_status',
            'total_amount',
            'created_at',
            'status',
            'address'
        ]