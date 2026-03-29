import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator

User = get_user_model()

class Category(models.Model):
    cat_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    image = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.cat_id:
            # Generate unique ID using UUID after C prefix
            unique_id = uuid.uuid4().hex[:6].upper()
            while Category.objects.filter(cat_id=f"C{unique_id}").exists():
                unique_id = uuid.uuid4().hex[:6].upper()
            self.cat_id = f"C{unique_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    originalPrice = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    sold = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    
    thumbnail = models.URLField(blank=True, null=True)
    images = ArrayField(
        base_field=models.URLField(),
        blank=True,
        null=True
    )

    ingredients = ArrayField(
        base_field=models.CharField(max_length=255),
        blank=True,
        null=True
    )
    preparationTime = models.CharField(max_length=50, blank=True, null=True)
    servingSize = models.CharField(max_length=50, blank=True, null=True)

    sizes = ArrayField(
        base_field=models.CharField(max_length=20),
        blank=True,
        null=True
    )
    color = ArrayField(
        base_field=models.CharField(max_length=20),
        blank=True,
        null=True
    )
    isAvailable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            unique_suffix = uuid.uuid4().hex[:6].upper()
            if self.category:
                cat_id = self.category.cat_id
                potential_id = f"{cat_id}-P{unique_suffix}"
                while Product.objects.filter(product_id=potential_id).exists():
                    unique_suffix = uuid.uuid4().hex[:6].upper()
                    potential_id = f"{cat_id}-P{unique_suffix}"
                self.product_id = potential_id
            else:
                self.product_id = f"P{unique_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Review(models.Model):
    review_id = models.CharField(max_length=25, unique=True, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    comment = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def save(self, *args, **kwargs):
        if not self.review_id:
            self.review_id = 'REV-' + uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.product.name} - {self.rating}"
