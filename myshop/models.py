from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

User = get_user_model()


class Category(models.Model):
    # Product category model
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    # Product model with category relation, stock, and image
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Order(models.Model):
    # Order model storing user, items JSON, payment status and Stripe info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.JSONField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    stripe_payment_intent = models.CharField(max_length=200, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {'Paid' if self.paid else 'Pending'}"


class Review(models.Model):
    # Review model linking user to product with rating and comment
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, f"{i} Stars") for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} for {self.product} - {self.rating} stars"
