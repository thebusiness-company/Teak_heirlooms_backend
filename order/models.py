from django.db import models
from django.conf import settings
from datetime import datetime
class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True, editable=False)
    cart = models.ForeignKey('product.Cart', on_delete=models.PROTECT, related_name='orders')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey('OrderAddress', on_delete=models.SET_NULL, null=True, blank=True)  
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if not self.order_id:
            today = datetime.today().strftime('%Y%m%d')
            # Use self._meta.model instead of hardcoded Order for better inheritance/flexibility
            count_today = self._meta.model.objects.filter(
                created_at__date=datetime.today().date()
            ).count() + 1
            self.order_id = f"ORD-{today}-{count_today:04d}"
        super().save(*args, **kwargs)
        
class OrderAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.city}"