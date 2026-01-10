from django.urls import path
from .views import *
urlpatterns = [
    path('orders/<int:order_id>/', get_order_details, name='get_order_details'),
    path('user/orders/', get_user_orders, name='get_user_orders'),
    path('create_order/', create_order, name='create_order'),
    path('verify_payment/', verify_payment, name='verify_payment'),
    path('cancel_payment/', cancel_payment, name='cancel_payment'),
    path('get_user_addresses/', get_user_addresses, name='get_user_addresses'),
    path("delete_user_address/", delete_user_address, name="delete_user_address"),

    #admin endpoints
    path('admin/orders/', admin_list_orders),
    path('admin/orders/<int:order_id>/', admin_get_order_details),
    path('admin/orders/<int:order_id>/update/', admin_update_order_status),
    path('admin/orders/<int:order_id>/delete/', admin_delete_order),

]