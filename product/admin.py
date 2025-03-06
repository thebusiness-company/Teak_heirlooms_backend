from django.contrib import admin

# Register your models here.
from .models import Product, RTShip

admin.site.register(Product)
admin.site.register(RTShip)
