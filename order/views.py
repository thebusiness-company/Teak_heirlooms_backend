import razorpay
import logging

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Order, OrderAddress
from product.models import Cart
from .serializers import OrderSerializer, AddressSerializer
from .permissions import IsAdminUserOnly

logger = logging.getLogger(__name__)

# Razorpay client
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# ======================================================
# CREATE ORDER (ADDRESS SAVED HERE)
# ======================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        cart_code = request.data.get('cart_code')
        amount = request.data.get('amount')  # amount in paise
        address_data = request.data.get('address')

        if not all([cart_code, amount, address_data]):
            return Response(
                {'error': 'cart_code, amount and address are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save address
        address_serializer = AddressSerializer(data=address_data)
        address_serializer.is_valid(raise_exception=True)
        address = address_serializer.save(user=request.user)

        # Get cart
        cart = Cart.objects.get(cart_code=cart_code)

        # Create Razorpay order
        razorpay_order = client.order.create({
            'amount': int(amount),
            'currency': 'INR',
            'payment_capture': 1
        })

        # Create order in DB
        order = Order.objects.create(
            user=request.user,
            cart=cart,
            address=address,
            razorpay_order_id=razorpay_order['id'],
            total_amount=int(amount) / 100,
            payment_status='pending'
        )

        return Response({
            'order_db_id': order.id,
            'order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'name': 'Teak Heirlooms',
            'description': 'Order Payment'
        }, status=status.HTTP_201_CREATED)

    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Create order error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ======================================================
# VERIFY PAYMENT
# ======================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    try:
        data = request.data

        required_fields = [
            'cart_code',
            'razorpay_payment_id',
            'razorpay_order_id',
            'razorpay_signature'
        ]

        if not all(data.get(field) for field in required_fields):
            return Response(
                {'error': 'Missing required payment fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify Razorpay signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })

        # Update order
        order = Order.objects.get(
            razorpay_order_id=data['razorpay_order_id'],
            cart__cart_code=data['cart_code']
        )

        order.razorpay_payment_id = data['razorpay_payment_id']
        order.razorpay_signature = data['razorpay_signature']
        order.payment_status = 'completed'
        order.save()

        # Mark cart as paid
        cart = order.cart
        cart.paid = True
        cart.save()

        return Response({
            'message': 'Payment verified successfully',
            'order_id': order.id
        }, status=status.HTTP_200_OK)

    except razorpay.errors.SignatureVerificationError:
        return Response(
            {'error': 'Invalid payment signature'},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Verify payment error: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ======================================================
# CANCEL PAYMENT
# ======================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_payment(request):
    try:
        cart_code = request.data.get('cart_code')
        razorpay_order_id = request.data.get('razorpay_order_id')

        if not cart_code or not razorpay_order_id:
            return Response(
                {'error': 'cart_code and razorpay_order_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

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


# ======================================================
# GET SINGLE ORDER
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Get order error: {str(e)}")
        return Response(
            {'error': 'Unable to fetch order'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ======================================================
# GET USER ORDERS
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Get user orders error: {str(e)}")
        return Response(
            {'error': 'Unable to fetch orders'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ======================================================
# USER ADDRESSES
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_addresses(request):
    addresses = OrderAddress.objects.filter(user=request.user)
    serializer = AddressSerializer(addresses, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_address(request):
    address_id = request.data.get('id')

    try:
        address = OrderAddress.objects.get(id=address_id, user=request.user)
        address.delete()
        return Response(
            {'message': 'Address deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )

    except OrderAddress.DoesNotExist:
        return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)


# Admin list all orders

@api_view(['GET'])
@permission_classes([IsAdminUserOnly])
def admin_list_orders(request):
    try:
        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Admin list orders error: {str(e)}")
        return Response(
            {'error': 'Unable to fetch orders'},
            status =status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Admin list single order details
@api_view(['GET'])
@permission_classes([IsAdminUserOnly])
def admin_get_order_details(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Admin Get order error: {str(e)}")
        return Response(
            {'error': 'Unable to fetch order'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['PATCH','PUT'])
@permission_classes([IsAdminUserOnly])
def admin_update_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        serializer = OrderSerializer(order,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e :
        logger.error(f"Admin Update order error: {str(e)}")
        return Response(
            {'error': 'Unable to update Order'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAdminUserOnly])
def admin_delete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
        return Response(
            {'message': 'Order deleted Successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e :
        logger.error(f"Admin Delete Order error: {str(e)}")
        return Response(
            {'error': 'Unable to delete Order'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )