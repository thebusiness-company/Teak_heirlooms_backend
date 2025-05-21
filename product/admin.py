from django.contrib import admin

# Register your models here.
from .models import Product, RTShip,Category,SubCategory

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(RTShip)
