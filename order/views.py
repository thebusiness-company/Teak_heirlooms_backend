import razorpay
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderAddress
from product.models import Cart
from .serializers import OrderSerializer, AddressSerializer
import json
# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@api_view(['POST'])
def create_order(request):
    try:
        cart_code = request.data.get('cart_code')
        amount = int(request.data.get('amount'))  # Amount in paise
        
        if not cart_code or not amount:
            return Response({'error': 'cart_code and amount are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Create Razorpay order
        razorpay_order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1  # Auto-capture payment
        })
        
        # Create order in database
        cart = Cart.objects.get(cart_code=cart_code)
        order = Order.objects.create(
            cart=cart,
            user=request.user if request.user.is_authenticated else None,
            razorpay_order_id=razorpay_order['id'],
            total_amount=amount / 100  # Convert back to rupees
        )
        
        return Response({
            'order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'name': 'Your Store Name',
            'description': 'Order Payment'
        })
        
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def verify_payment(request):
    try:
        data = request.data
        cart_code = data.get('cart_code')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        address_data = data.get('address')
        
        if not all([cart_code, razorpay_payment_id, razorpay_order_id, razorpay_signature, address_data]):
            return Response({'error': 'Missing required data'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
        except Exception as e:
            return Response({'error': 'Invalid payment signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order with payment details
        order = Order.objects.get(razorpay_order_id=razorpay_order_id, cart__cart_code=cart_code)
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.payment_status = 'completed'
        order.save()
        
        # Mark cart as paid
        cart = order.cart
        cart.paid = True
        cart.save()
        
        # Save address
        address_serializer = AddressSerializer(data=address_data)
        if address_serializer.is_valid():
            address = address_serializer.save(user=request.user if request.user.is_authenticated else None)
            order.address = address
            order.save()
        else:
            return Response({'error': address_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Payment verified and order created successfully', 'order_id': order.id})
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_user_addresses(request):
    if request.user.is_authenticated:
        addresses = OrderAddress.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)
    return Response([], status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_address(request):
    address_id = request.data.get("id")
    try:
        address = OrderAddress.objects.get(id=address_id, user=request.user)
        address.delete()
        return Response({"message": "Address deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except OrderAddress.DoesNotExist:
        return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def cancel_payment(request):
    try:
        cart_code = request.data.get('cart_code')
        razorpay_order_id = request.data.get('razorpay_order_id')
        
        if not cart_code or not razorpay_order_id:
            return Response({'error': 'cart_code and razorpay_order_id are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        order = Order.objects.get(
            razorpay_order_id=razorpay_order_id,
            cart__cart_code=cart_code,
            payment_status='pending'
        )
        order.payment_status = 'cancelled'
        order.save()
        
        return Response({'message': 'Order cancelled successfully'})
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

from .models import Order
from product.models import Cart
from .serializers import OrderSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        
        # Ensure the order belongs to the current user if authenticated
        if request.user.is_authenticated and order.user != request.user:
            return Response(
                {'error': 'You do not have permission to view this order'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = OrderSerializer(order)
        return Response(serializer.data)
        
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching order details: {str(e)}")
        return Response(
            {'error': 'An error occurred while fetching order details'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_user_orders(request):
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching user orders: {str(e)}")
        return Response(
            {'error': 'An error occurred while fetching your orders'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )