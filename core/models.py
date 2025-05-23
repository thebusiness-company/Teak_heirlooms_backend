from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=150)
    address = models.CharField(max_length=150,blank=True,null=True)
    city = models.CharField(max_length=150,blank=True,null=True)
    state = models.CharField(max_length=150,blank=True,null=True)
    zip_code = models.CharField(max_length=150,blank=True,null=True)
    country = models.CharField(max_length=150,default='india')
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country','profile_picture','gender','date_of_birth']
    
    def __str__(self):
        return self.email
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
class Testimonial(models.Model):
    image = models.ImageField(upload_to='testimonials/')
    title = models.CharField(max_length=255)
    text = models.TextField()
    name = models.CharField(max_length=100)
    rating = models.IntegerField(default=5)

    def __str__(self):
        return self.title
    
class HomeBanner(models.Model):
    image = models.ImageField(upload_to="homebanners/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Banner {self.id} - {self.uploaded_at}"
    
class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='blogs/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class VideoBanner(models.Model):
    youtube_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.youtube_url
    

class ShopMainBanner(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_text = models.CharField(max_length=100)
    image_left = models.ImageField(upload_to="banners/")
    image_right = models.ImageField(upload_to="banners/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title