from rest_framework import serializers
from .models import Testimonial, VideoBanner, HomeBanner, Blog, ShopMainBanner

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'
class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields = ['id', 'image', 'uploaded_at']

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'image']

class VideoBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoBanner
        fields = '__all__'


class ShopMainBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopMainBanner
        fields = "__all__"