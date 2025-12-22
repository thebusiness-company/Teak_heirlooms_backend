from django.db import models

from django.utils.text import slugify
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name="subcategories", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True, null=True, unique=True)
    image = models.ImageField(upload_to="subcategories/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "SubCategories"
        unique_together =('name', 'category')

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class ShopCollection(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_trending = models.BooleanField(default=False, help_text="Check if this is a trending item")
    image = models.ImageField(upload_to='shop_collections/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: specific ID string (e.g., "collection1") if you want to keep exact frontend logic
    # Otherwise, Django uses auto-incrementing Integers (1, 2, 3)
    custom_id = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="e.g., collection1")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']

class Product(models.Model):
    
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    collection = models.ForeignKey(ShopCollection, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    trending = models.BooleanField(default=False)
    topselling = models.BooleanField(default=False)
    newin = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    ratings = models.FloatField(default=0.0)
    dimensions = models.JSONField(default=dict,blank=True,null=True)
    customizable = models.BooleanField(default=False)
    newarrived = models.BooleanField(default=False)
    mostsold = models.BooleanField(default=False)
    finishes = models.JSONField(default=list,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/images/")

    def __str__(self):
        return f"Image for {self.product.name}"

class RTShip(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rtship', )
    NewArrival = models.BooleanField(default=False)
    MostSold = models.BooleanField(default=False)

class Room(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='rooms/')
    products = models.ManyToManyField(Product, related_name='rooms', blank=True)

    def __str__(self):
        return self.name
    
   

class Cart(models.Model):
    cart_code = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,blank=True, null=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.cart_code
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    finishes = models.CharField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return f'{self.quantity}*{self.product.name} in {self.cart.id}'
    