from django import forms
from django.db import models
from django.contrib.auth.models import User
from numpy import product

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, null = True,blank=True ,on_delete=models.CASCADE)
    phone = models.CharField(max_length=200, null=True )
    profile_pic = models.ImageField(default="profile.png",null = True,blank = True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user = instance)
        print('Profile created')


def update_profile(sender, instance, created, **kwargs):
    if created == False:
        instance.UserProfile.save()
        print('Profile Updated')

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category =  models.ForeignKey(Category, null=True, on_delete= models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    img = models.ImageField(default="product-pic.jpg",null = True,blank = True)

    def __str__(self):
        return self.name

class Color(models.Model):
    color = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.color

class Size(models.Model):
    size = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.size

class Product(models.Model):
    name = models.CharField(max_length=200,blank = True, null=True)
    price = models.FloatField(default=0,null=True)
    category = models.ManyToManyField(Category)
    subcategory = models.ManyToManyField(SubCategory)
    color = models.ManyToManyField(Color)
    size = models.ManyToManyField(Size)
    product_code = models.CharField(max_length=200, null=True,blank=True)
    description = models.TextField(max_length=2000, null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    stock = models.IntegerField(default=0, null = True,blank = True)
    discount = models.IntegerField(default=0, null = True,blank = True)
    discount_amount = models.FloatField(default=0, null = True,blank = True)
    rate = models.FloatField(default=0, null = True,blank = True)
    featured = models.BooleanField(default=False,blank=True,null=True)

    def __str__(self):
        return self.name

class ProductImages(models.Model):
    product =  models.ForeignKey(Product, null=True, on_delete= models.CASCADE)
    n_img = models.ImageField(default="product-pic.jpg",null = True,blank = True)
    Z_img = models.ImageField(default="product-pic.jpg",null = True,blank = True)

    def __str__(self):
        return self.product.name

class Subscription(models.Model):
    email = models.EmailField(null = True,blank = True)

    def __str__(self):
        return self.email

class Review(models.Model):
    user = models.ForeignKey(Customer, models.CASCADE)
    product = models.ForeignKey(Product, models.CASCADE)
    comment = models.TextField(max_length=250)
    rate = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class ReviewImages(models.Model):
    review =  models.ForeignKey(Review, null=True, on_delete= models.CASCADE)
    img = models.ImageField(default="product-pic.jpg",null = True,blank = True)

    def __str__(self):
        return str(self.img)

class PopularFurniture(models.Model):
    user = models.ForeignKey(User, null = True,blank=True ,on_delete=models.CASCADE)
    category_for =  models.CharField(max_length=200,blank=True, null=True)
    categorys = models.ManyToManyField(SubCategory)


class IndivitualCategory(models.Model):
    user = models.ForeignKey(User, null = True,blank=True ,on_delete=models.CASCADE)
    category_for =  models.CharField(max_length=200,blank=True, null=True)
    categorys = models.ManyToManyField(Category)

    def __str__(self):
        return self.category_for

class HomeBannerCategory(models.Model):
    title_heading =  models.CharField(max_length=200,blank=True, null=True)
    estimated_category = models.OneToOneField(Category, on_delete= models.CASCADE)
    banner_img = models.ImageField(default="product-pic.jpg",null = True,blank = True)

    def __str__(self):
        return self.title_heading

class CollectionCategory(models.Model):
    estimated_category = models.OneToOneField(Category, on_delete= models.CASCADE)
    img = models.ImageField(default="product-pic.jpg",null = True,blank = True)

    def __str__(self):
        return self.estimated_category.name

class ShopNowCategorys(models.Model):
    img = models.ImageField(default="product-pic.jpg",null = True,blank = True)
    estimated_category = models.OneToOneField(SubCategory,blank=True, null=True, on_delete= models.CASCADE)

    def __str__(self):
        return self.estimated_category.name

class Blog(models.Model):
    name = models.CharField(max_length=200,blank=True, null=True)
    place = models.CharField(max_length=200,blank=True, null=True)
    description = models.TextField(max_length=2000,blank=True, null=True)
    img = models.ImageField(default="product-pic.jpg",null = True,blank = True)
    video = models.FileField(null = True,blank = True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    STATUS = (
        ('Pending','Pending'),
        ('Customer Confirmed','Customer Confirmed'),
        ('Admin Confirmed','Admin Confirmed'),
        ('In-Transit', 'In-Transit'),
        ('Delivered','Delivered'),
        ('Return','Return'),
        ('Cancel','Cancel')
    )
    customer = models.ForeignKey(Customer, null=True, on_delete= models.CASCADE)
    complete = models.BooleanField(default=False)
    cupon_code =  models.CharField(default="None",max_length=200,blank=True, null=True)
    cupon_amount = models.FloatField(default=0,blank=True,null=True)
    transaction_id = models.CharField(max_length=200, null=True)
    method = models.CharField(max_length=200, null=True)
    member_amount = models.FloatField(default=0,blank=True,null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    delivery_fee = models.FloatField(default=0,blank=True,null=True)
    total = models.FloatField(default=0,blank=True,null=True)
    advance = models.FloatField(default=0,blank=True,null=True)
    due = models.FloatField(default=0,blank=True,null=True)
    status = models.CharField(default="Pending",max_length=200,blank=True, null=True,choices=STATUS)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    

class WishList(models.Model):
    customer =  models.OneToOneField(Customer, on_delete= models.CASCADE)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.customer.phone

class Delivery_charge(models.Model):
    w_delivery = models.CharField(blank=True,null=True, max_length=100)
    fee = models.FloatField(default=0,blank=True,null=True)
    discount = models.IntegerField(default=0,blank=True,null=True)

class OrderItem(models.Model):
    customer = models.ForeignKey(Customer, null=True, on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)
    rate = models.FloatField(default=0,blank=True,null=True)
    total = models.FloatField(default=0,blank=True,null=True)
    color = models.CharField(blank=True,null=True, max_length=100)
    size = models.CharField(blank=True,null=True, max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.city

class Cupon(models.Model):
    cupon_code = models.CharField(blank=True,null=True, max_length=100)
    amount = models.FloatField(default=0,blank=True,null=True)

    def __str__(self):
        return self.cupon_code

class LatestArrivals(models.Model):
    user = models.ForeignKey(User, null = True,blank=True ,on_delete=models.CASCADE)
    products_for =  models.CharField(max_length=200,blank=True, null=True)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.products_for

class DiscountDetails(models.Model):
    category = models.ForeignKey(Category, null = True,blank=True ,on_delete=models.CASCADE)
    name =  models.CharField(max_length=200,blank=True, null=True)
    percentage = models.IntegerField(default=0,null=True,blank=True)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.name