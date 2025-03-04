from django.contrib import admin
from .models import CustomUser, Testimonial, HomeBanner, Blog

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country', 'date_joined', 'last_login', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country', 'date_joined', 'last_login', 'is_active', 'is_staff']
    list_filter = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country', 'date_joined', 'last_login', 'is_active', 'is_staff']
# Register your models here.

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Testimonial)
admin.site.register(HomeBanner)
admin.site.register(Blog)
