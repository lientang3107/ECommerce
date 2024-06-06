from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.db.models import Avg



class User(AbstractUser):
    avatar = CloudinaryField(type='upload', resource_type='image', default=None)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    SELLER_ROLE = 'seller'
    CUSTOMER_ROLE = 'customer'
    ROLE_CHOICES = [
        (SELLER_ROLE, 'Seller'),
        (CUSTOMER_ROLE, 'Customer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER_ROLE)

    def __str__(self):
        return self.username



class Category(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    image = CloudinaryField(type='upload', resource_type='image', default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.product:
            return f"{self.user.username} - {self.product.product_name}"
        elif self.store:
            return f"{self.user.username} - {self.store.store_name}"

class Store(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    wallpaper = CloudinaryField(type='upload', resource_type='image', default=None)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.store_name

    def average_rating(self):
        return self.review_set.aggregate(Avg('rating'))['rating__avg']


class Product(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = RichTextField()
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.product_name

    def average_rating(self):
        return self.review_set.aggregate(Avg('rating'))['rating__avg']




class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images+')
    image = CloudinaryField(type='upload', resource_type='image', default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Product Variant - ID: {self.id}, Product ID: {self.product_id}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, default=None)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('paypal', 'Paypal'),
        ('stripe', 'Stripe'),
        ('zalopay', 'ZaloPay'),
        ('momo', 'MoMo'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)



class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, default=None)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, default=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)

class Payment(models.Model):
    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)

