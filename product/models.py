from django.db import models

from django.utils.text import slugify

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Sofas', 'Sofas'),
        ('Beds', 'Beds'),
        ('Tables', 'Tables'),
        ('Book Shelf', 'Book Shelf'),
        ('Cabinet', 'Cabinet'),
        ('Dining', 'Dining'),
        ('Bar', 'Bar'),
        ('Pooja', 'Pooja'),
        ('TV Units', 'TV Units'),
        ('Wardrobe', 'Wardrobe'),
        ('Wall Panels', 'Wall Panels'),
        ('Paintings', 'Paintings'),
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    price = models.FloatField()
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    trending = models.BooleanField(default=False)
    topselling = models.BooleanField(default=False)
    newin = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


class RTShip(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rtship', )
    NewArrival = models.BooleanField(default=False)
    MostSold = models.BooleanField(default=False)
