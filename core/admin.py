from django.contrib import admin
from .models import *

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country', 'date_joined', 'last_login', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country', 'date_joined', 'last_login', 'is_active', 'is_staff']
    list_filter = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country', 'date_joined', 'last_login', 'is_active', 'is_staff']
# Register your models here.

admin.site.register([CustomUser, Testimonial, HomeBanner, Blog, ShopMainBanner, VideoBanner, HomeCategory])
