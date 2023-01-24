from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import *
from .utils import *
from .forms import *
from .decorators import *
import math
import json
import datetime

# Create your views here.
def logoutUser(request):
    logout(request)
    return redirect('noksha:home')

def loginUser(request):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #CartItem Section
    cookieData = cookieCart(request)
    cartItems = cookieData['cartItems']
    cartTotal = cookieData['cartTotal']
    order = cookieData['order']
    items = cookieData['items']
    total_items = len(items)
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0

    #Login Section
    if request.method =='POST' and 'login_username' in request.POST:
        login_username = request.POST.get('login_username')
        password = request.POST.get('login_password')

        try:
            user_1 = User.objects.get(username = login_username)
            username = user_1.username
        except:
            customer_1 = Customer.objects.get(phone = login_username)
            user_1 =  customer_1.user
            username = user_1.username

        user = authenticate(request,username=username, password=password)
        login(request,user)
        if user_1.groups.all()[0].name == 'admin':
            return redirect('noksha:shop_dashboard')
        if user is not None:
            customer = Customer.objects.get(phone = login_username)
            shipping = ShippingAddress.objects.get(customer = customer)
            db_order, created = Order.objects.get_or_create(customer=customer, complete=False)
            db_order.cupon_code = order['cupon_code']
            db_order.cupon_amount = order['cupon_amount']
            db_order.address = shipping.address
            db_order.city = shipping.city
            db_order.state = shipping.state
            db_order.save()
            for item in items:
                product = Product.objects.get(id=item['product']['id'])
                quantity = item['quantity']
                rate = product.price
                total = float(product.price) * float(quantity)
                orderItem, created  = OrderItem.objects.get_or_create(
                    product=product,
                    order = db_order,
                    customer=customer
                )
                orderItem.quantity=item['quantity']
                orderItem.size = item['size']
                orderItem.color = item['color']
                orderItem.rate = rate,
                orderItem.total = total
                orderItem.save()
            messages.success(request,'Login Successfull!')
            return redirect('noksha:home')
        else:
            messages.error(request,'Login failed. Please try again!')
            return redirect('noksha:login')
    if total_items > 0:
        for item in items:
            product = Product.objects.get(id = item['product']['id'])
            item['sizes'] = product.size.all()
            item['colors'] = product.color.all()
            item['image'] = ProductImages.objects.filter(product = product)[:1]
            price_total += product.price
    
        total = float(price_total) + float(delivery_charge)

        context ={
            'cartItems':cartItems,
            'cartTotal':cartTotal,
            'nvCategorys':navbarCategorys,
            'order':order,
            'items':items,
            'item.image':item['image'],
            'item.sizes':item['sizes'],
            'item.colors':item['colors'],
            'delivery_charge':delivery_charge,
            'total':total,

        }
    else:
        context ={
            'cartItems':cartItems,
            'cartTotal':cartTotal,
            'nvCategorys':navbarCategorys,

        }
    return render(request,'accounts/login.html',context)

def signUpUser(request):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #CartItem Section
    cookieData = cookieCart(request)
    cartItems = cookieData['cartItems']
    cartTotal = cookieData['cartTotal']
    order = cookieData['order']
    items = cookieData['items']
    total_items = len(items)
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0

    #SignUp Section
    if request.method =='POST' and 'reg_name' in request.POST:
        name =  request.POST.get('reg_name')
        email =  request.POST.get('reg_email')
        phone =  request.POST.get('reg_phone')
        password1 =  request.POST.get('reg_password1')
        password2 =  request.POST.get('reg_password2')
        address =  request.POST.get('address')
        area =  request.POST.get('area')
        city =  request.POST.get('city')
        if User.objects.filter(email=email).first():
            messages.error(request, 'Email is taken.')
            return redirect('noksha:sign_up')
        elif Customer.objects.filter(phone = phone).first():
            messages.error(request, 'Phone is used on another account.')
            return redirect('noksha:sign_up')
        elif password1 != password2:
            messages.error(request, "Password didn't match!.")
            return redirect('noksha:sign_up')
        else:
            user = User.objects.create(first_name = name, email=email,username=phone)
            user.set_password(password1)
            user.save()
            customer = Customer.objects.create(
                    user = user,
                    phone = phone,
            )
            shipping =  ShippingAddress.objects.create(
                customer = customer,
                address = address,
                state = area,
                city = city
            )
            group = Group.objects.get(name = 'customer')
            user.groups.add(group)
            if user is not None:
                db_order, created = Order.objects.get_or_create(customer=customer, complete=False)
                db_order.address = shipping.address
                db_order.city = shipping.city
                db_order.state = shipping.state
                db_order.save()
                for item in items:
                    product = Product.objects.get(id=item['product']['id'])
                    quantity = item['quantity']
                    rate = product.price
                    total = float(product.price) * float(quantity)
                    orderItem, created  = OrderItem.objects.get_or_create(
                       product=product,
                        order = db_order,
                        customer=customer, 
                        )
                    orderItem.quantity=item['quantity']
                    orderItem.size = item['size']
                    orderItem.color = item['color']
                    orderItem.rate = rate,
                    orderItem.total = total
                    orderItem.save()
                login(request,user)
            messages.success(request,'Login Successfull!')
        return redirect('noksha:home')
    
    if total_items > 0:
        for item in items:
            product = Product.objects.get(id = item['product']['id'])
            item['sizes'] = product.size.all()
            item['colors'] = product.color.all()
            item['image'] = ProductImages.objects.filter(product = product)[:1]
            price_total += product.price
    
        total = float(price_total) + float(delivery_charge)

        context ={
            'cartItems':cartItems,
            'cartTotal':cartTotal,
            'nvCategorys':navbarCategorys,
            'order':order,
            'items':items,
            'item.image':item['image'],
            'item.sizes':item['sizes'],
            'item.colors':item['colors'],
            'delivery_charge':delivery_charge,
            'total':total,

        }
    else:
        context ={
            'cartItems':cartItems,
            'cartTotal':cartTotal,
            'nvCategorys':navbarCategorys,

        }
    return render(request,'accounts/registration.html',context)

@login_required(login_url='noksha:login')
def accountProfile(request,pk):
    user = request.user
    customer = request.user.customer
    user_orders = Order.objects.filter(customer=customer,complete = True).order_by('-date_created')

    #Status Section 
    total_orders = user_orders.count()
    delivered = user_orders.filter(status = 'Delivered').count()
    transit = user_orders.filter(status = 'In-Transit').count()
    confirmed = user_orders.filter(status = 'Admin Confirmed').count()
    pending = user_orders.filter(status = 'Customer Confirmed').count()
    
    status = {
        'total_orders':total_orders,
        'delivered':delivered,
        'transit':transit,
        'confirmed':confirmed, 
        'pending':pending,
    }

    #Wish List Section
    wish_products = []
    total_wish_products = 0
    if WishList.objects.filter(customer = customer).exists():
        wish_object = WishList.objects.get(customer = customer)
        for i in wish_object.products.all():
            wish_products.append(productSerialize(i.id))
        total_wish_products = wish_object.products.all().count()

    wish_list = {
        'total_products': total_wish_products,
        'wish_products':wish_products,
    }
    if request.method == 'POST' and 'remove_wish' in request.POST:
        remove_wish = request.POST.get('remove_wish')
        wish_remove_product = Product.objects.get(id = remove_wish)
        wish_remove_object = WishList.objects.get(customer = request.user.customer)
        wish_remove_object.products.remove(wish_remove_product)
        messages.success(request,'Product successfully removed from wish list!')
        return redirect(reverse('noksha:account_profile', kwargs={'pk':pk}))

    #Shipping Section
    shipping = ShippingAddress.objects.get(customer = customer)

    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Account Edit Section
    if request.method == 'POST'and 'account_name' in request.POST:
        account_name = request.POST.get('account_name')
        account_email = request.POST.get('account_email')
        account_telephone = request.POST.get('account_telephone')
        account_image = request.FILES.get('account_image')
        user.first_name = account_name
        user.email = account_email
        if User.objects.filter(username = account_telephone).exclude(username = user.username).exists():
            messages.error(request,'Account exists with this phone number!')
            return redirect(reverse('noksha:account_profile', kwargs={'pk':pk}))
        elif Customer.objects.filter(phone = account_telephone).exclude(phone = customer.phone).exists():
            messages.error(request,'Account exists with this phone number!')
            return redirect(reverse('noksha:account_profile', kwargs={'pk':pk}))
        else:
            user.username = account_telephone

        user.save()
        if account_image is not None:
            customer.phone = account_telephone
            customer.profile_pic = account_image
        else:
            customer.phone = account_telephone
        customer.save()
        messages.success(request,'Information updated!')
        return redirect(reverse('noksha:account_profile', kwargs={'pk':pk}))

    if request.method == 'POST' and 'old_password' in request.POST:
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password1')
        if check_password(old_password,user.password):
            if new_password1 != new_password2:
                messages.error(request,"Password didn't match. Please enter it again.")
            elif new_password1 == old_password:
                messages.error(request,"New password can't be as same as old password.")
            else:
                user.set_password(new_password1)
                user.save()
                login(request,user)
                messages.success(request,'Password updated!')
        else:
            messages.error(request,'Your old password was entered incorrectly. Please enter it again.')

        return redirect(reverse('noksha:account_profile', kwargs={'pk':pk}))
    
    if request.method == 'POST' and 'address' in request.POST:
        address = request.POST.get('address')
        state = request.POST.get('state')
        city = request.POST.get('city')
        shipping.address = address
        shipping.state = state
        shipping.city = city
        shipping.save()
        messages.success(request,'Billing details updated!')
        return redirect(reverse('noksha:account_profile', kwargs={'pk':pk}))

    #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'status':status,
                'filterOrders':user_orders,
                'wish_list':wish_list,
                'nvCategorys':navbarCategorys,
                'shipping':shipping,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'status':status,
                'filterOrders':user_orders,
                'wish_list':wish_list,
                'nvCategorys':navbarCategorys,
                'shipping':shipping,
                'cartItems':cartItems,
            }
    return render(request,'accounts/accountProfile.html',context)

def home(request):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Member Discount
    if request.method == 'POST' and 'subscribe_email' in request.POST:
        subscribe_email = request.POST.get('subscribe_email')
        if Subscription.objects.filter(email= subscribe_email).exists():
            messages.error(request,'This email already subscribed!')
            return redirect('noksha:home')
        else:
            Subscription.objects.create(email = subscribe_email)
            messages.success(request,'Subscription successfull!')
            return redirect('noksha:home')



    total_products = Product.objects.all().count()
    if total_products > 0:

        #Home Banner Section
        homeBannerCategoryWithImage = HomeBannerCategory.objects.all()[:3]

        #Collection Category Section
        collectionCategoryWithImage = CollectionCategory.objects.all()[:6]

        #ShopNow Category Section
        shopNowCategoryWithImage = ShopNowCategorys.objects.all()[:6]

        #Blog Section
        blogs = []
        tmp_blogs = Blog.objects.all().order_by('-date_added')
        for i in tmp_blogs:
            blogs.append(blogs_with_detailed_date(i.id))

        # Most Viewed Section
        mostViewedCategoryObject = PopularFurniture.objects.get(category_for = 'pvfurniture')
        mostViewedCategorys = mostViewedCategoryObject.categorys.all()

        #Latest Arrivals Section
        latestArrivalsProductsObject = LatestArrivals.objects.get(products_for = 'latestarrivals')
        latestArrivalsProductsInLoop = latestArrivalsProductsObject.products.all()
        latestArrivalsProducts = []
        for i in latestArrivalsProductsInLoop:
            latestArrivalsProducts.append(productSerialize(i.id))

        #Cart Item Section
        delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
        delivery_charge = delivery_charge_object.fee
        price_total = 0
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.get_cart_items
            cartTotal = order.get_cart_total
            items = order.orderitem_set.all()
            total_items = items.count()
            if total_items> 0:
                for item in items:
                    product = Product.objects.get(id = item.product.id)
                    item.sizes = product.size.all()
                    item.colors = product.color.all()
                    item.image = ProductImages.objects.filter(product = product)[:1]
                    price_total += product.price
            
                total = float(price_total) + float(delivery_charge)
                context = {
                    'blogs':blogs,
                    'sncimage':shopNowCategoryWithImage,
                    'ccimage':collectionCategoryWithImage,
                    'hbcimage':homeBannerCategoryWithImage,
                    'ltproducts':latestArrivalsProducts,
                    'nvCategorys':navbarCategorys,
                    'mvCategorys':mostViewedCategorys,
                    'items':items,
                    'cartItems':cartItems,
                    'cartTotal':cartTotal,
                    'order':order,
                    'item.image':item.image,
                    'item.sizes':item.sizes,
                    'item.colors':item.colors,
                    'delivery_charge':delivery_charge,
                    'total':total,
                }
            else:
                context = {
                    'blogs':blogs,
                    'sncimage':shopNowCategoryWithImage,
                    'ccimage':collectionCategoryWithImage,
                    'hbcimage':homeBannerCategoryWithImage,
                    'ltproducts':latestArrivalsProducts,
                    'nvCategorys':navbarCategorys,
                    'mvCategorys':mostViewedCategorys,
                    'cartItems':cartItems,
                }

        else:
            cookieData = cookieCart(request)
            cartItems = cookieData['cartItems']
            cartTotal = cookieData['cartTotal']
            order = cookieData['order']
            items = cookieData['items']
            total_items = len(items)

            if total_items > 0:

                for item in items:
                    product = Product.objects.get(id = item['product']['id'])
                    item['sizes'] = product.size.all()
                    item['colors'] = product.color.all()
                    item['image'] = ProductImages.objects.filter(product = product)[:1]
                    price_total += product.price
            
                total = float(price_total) + float(delivery_charge)
                context = {
                    'blogs':blogs,
                    'sncimage':shopNowCategoryWithImage,
                    'ccimage':collectionCategoryWithImage,
                    'hbcimage':homeBannerCategoryWithImage,
                    'ltproducts':latestArrivalsProducts,
                    'mvCategorys':mostViewedCategorys,
                    'nvCategorys':navbarCategorys,
                    'items':items,
                    'cartItems':cartItems,
                    'cartTotal':cartTotal,
                    'order':order,
                    'item.image':item['image'],
                    'item.sizes':item['sizes'],
                    'item.colors':item['colors'],
                    'delivery_charge':delivery_charge,
                    'total':total,
                }
            else:
                context = {
                    'blogs':blogs,
                    'sncimage':shopNowCategoryWithImage,
                    'ccimage':collectionCategoryWithImage,
                    'hbcimage':homeBannerCategoryWithImage,
                    'ltproducts':latestArrivalsProducts,
                    'nvCategorys':navbarCategorys,
                    'mvCategorys':mostViewedCategorys,
                    'cartItems':cartItems,
                }

    else:
        context = {
            'nvCategorys':navbarCategorys,
        }
    return render(request,'store/pages/home.html',context)

def productView(request,pk):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    product = Product.objects.get(id = pk)
    images = ProductImages.objects.filter(product=product)
    big_img = ProductImages.objects.filter(product=product)[:1]
    demo_price = 0
    if product.discount > 0:
        demo_price = product.price + product.discount_amount
    #WishList Section
    if request.user.is_authenticated:
        wish_customer = request.user.customer
        if request.method == 'POST' and 'wish-List' in request.POST:
            wish_product = request.POST.get('wish-List')
            if WishList.objects.filter(customer = wish_customer).exists():
                wish_object = WishList.objects.get(customer = wish_customer)
            else:
                wish_object = WishList.objects.create(customer = wish_customer)
            wish_object.products.add(wish_product)
            wish_object.save()
            messages.success(request,'Product added to Wish List!')
            return redirect(reverse('noksha:product_view', kwargs={'pk':pk}))

            

    #Review Section
    reviews = []
    tmp_reviews = Review.objects.filter(product=product)
    total_review = tmp_reviews.count()
    review_count = 0
    for i in tmp_reviews:
        reviews.append(reviews_with_images(i.id))
        review_count += i.rate
        product.rate = float(review_count/total_review)
        product.save()

    if request.method == 'POST' and 'review_comment' in request.POST:
        comment = request.POST.get('review_comment')
        rate = request.POST.get('review_rate')
        review_images = request.FILES.getlist('review_images')
        new_review = Review.objects.create(user = request.user.customer, product = product)
        new_review.comment = comment
        new_review.rate = rate
        new_review.save()
        for i in review_images:
            new_image = ReviewImages.objects.create(review = new_review,img = i)
        
        messages.success(request,'Review added successfully!')
        return redirect(reverse('noksha:product_view', kwargs={'pk':pk}))

    #Releted Product Section
    categorys = product.category.all()
    reletedProducts = []
    for i in categorys:
        category_product = Product.objects.filter(category=i).order_by('-rate')
        for j in category_product:
            reletedProducts.append(productSerialize(j.id))

    #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'product':product,
                'nvCategorys':navbarCategorys,
                'images':images,
                'big_img':big_img,
                'reviews':reviews,
                'total_review':total_review,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'demo_price':demo_price,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
                'rltdProducts':reletedProducts,
            }
        else:
            context = {
                'product':product,
                'demo_price':demo_price,
                'nvCategorys':navbarCategorys,
                'images':images,
                'big_img':big_img,
                'reviews':reviews,
                'total_review':total_review,
                'cartItems':cartItems,
                'rltdProducts':reletedProducts,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        total_items = len(items)

        if total_items > 0:

            for item in items:
                product = Product.objects.get(id = item['product']['id'])
                item['sizes'] = product.size.all()
                item['colors'] = product.color.all()
                item['image'] = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'product':product,
                'nvCategorys':navbarCategorys,
                'images':images,
                'big_img':big_img,
                'reviews':reviews,
                'total_review':total_review,
                'items':items,
                'demo_price':demo_price,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item['image'],
                'item.sizes':item['sizes'],
                'item.colors':item['colors'],
                'delivery_charge':delivery_charge,
                'total':total,
                'rltdProducts':reletedProducts,
            }
        else:
            context = {
                'product':product,
                'demo_price':demo_price,
                'nvCategorys':navbarCategorys,
                'images':images,
                'big_img':big_img,
                'reviews':reviews,
                'total_review':total_review,
                'cartItems':cartItems,
                'rltdProducts':reletedProducts,
            }

    return render(request,'store/pages/productview.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productID']
    action = data['action']
    color = data['color']
    size = data['size']
    quantity = data['quantity']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(customer=customer, order=order,  product=product)
    if size and color != "undefined":
       orderItem.color = color
       orderItem.size = size

    if quantity == 'undefined':
        quantity = 1

    orderItem.rate = product.price

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + int(quantity))

    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    elif action == 'delete':
        orderItem.quantity = 0
    
    elif action == 'color':
        orderItem.color = color
    
    elif action == 'size':
        orderItem.size = size
    
    orderItem.total = (orderItem.quantity * product.price)
            
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    

    return JsonResponse('Item was added', safe=False)


def cart(request):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Member Discount
    if request.method == 'POST' and 'subscribe_email' in request.POST:
        subscribe_email = request.POST.get('subscribe_email')
        if Subscription.objects.filter(email= subscribe_email).exists():
            messages.error(request,'This email already subscribed!')
            return redirect('noksha:cart')
        else:
            Subscription.objects.create(email = subscribe_email)
            messages.success(request,'Subscription successfull!')
            return redirect('noksha:cart')
    
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    related_categorys = []
    related_products = []

    # Related products 
    for i in related_categorys:
        products = Product.objects.filter(category = i)
        for j in products:
            related_products.append(productSerialize(j.id))

    if request.user.is_authenticated:
        try:
            cupon_d = json.loads(request.COOKIES.get('cupon'))
            cupon_code = cupon_d['cupon_code']
            cupon_exits = Cupon.objects.filter(cupon_code = cupon_code).count()
            if cupon_exits == 1:
                cupon_object = Cupon.objects.get(cupon_code = cupon_code)
                cupon = cupon_object.cupon_code
                amount = cupon_object.amount
            else:
                cupon = "None"
                amount = 0
        except:
            
            cupon = "None"
            amount = 0

        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        order.cupon_code = cupon
        order.cupon_amount = amount
        order.save()
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                categorys = product.category.all()
                for i in categorys:
                    related_categorys.append(i)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]

            total = float(cartTotal) + float(delivery_charge) - float(order.cupon_amount)


            context = {
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'nvCategorys':navbarCategorys,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
                'related_products':related_products
            }
           
        else:
            context = {
                'items':items,
                'nvCategorys':navbarCategorys,
                'cartItems':cartItems,
                'order':order,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        total_items = len(items)

        if total_items > 0:

            for item in items:
                product = Product.objects.get(id = item['product']['id'])
                categorys = product.category.all()
                for i in categorys:
                    related_categorys.append(i)
                item['sizes'] = product.size.all()
                item['colors'] = product.color.all()
                item['image'] = ProductImages.objects.filter(product = product)[:1]

            total = float(cartTotal) + float(delivery_charge) - float(order['cupon_amount'])

            context = {
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'nvCategorys':navbarCategorys,
                'order':order,
                'item.image':item['image'],
                'item.sizes':item['sizes'],
                'item.colors':item['colors'],
                'delivery_charge':delivery_charge,
                'total':total,
                'related_products':related_products
            }
            
        else:
            context = {
                'items':items,
                'cartItems':cartItems,
                'nvCategorys':navbarCategorys,
                'cartTotal':cartTotal,
                'order':order,
            }
    
    

    return render(request,'store/pages/cart.html',context)


def checkout(request):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    delivery_charge = 60
    
    shipping = None
    member = False
    percentageAmount = 0
    
        
    if request.user.is_authenticated:
        
        customer = request.user.customer
        shipping = ShippingAddress.objects.get(customer = customer)
        if shipping.city == 'Dhaka':
            delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
            delivery_charge = delivery_charge_object.fee

        else:
            delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Other')
            delivery_charge = delivery_charge_object.fee

        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        if Order.objects.filter(customer=customer,complete=True,cupon_code = order.cupon_code).exists():
            order.cupon_code += '- expired'
            order.cupon_amount = 0
            order.save()
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        if Subscription.objects.filter(email = request.user.email).exists():
            member = True
            percentageAmount = math.floor(float(cartTotal) * 0.05)

        items = order.orderitem_set.all()
        bkash_total = math.ceil(float(cartTotal) + float(cartTotal * 0.02) - float(order.cupon_amount) - float(percentageAmount) + float(delivery_charge)) 
        nagad_total = math.ceil(float(cartTotal) + float(cartTotal * 0.01494) - float(order.cupon_amount) - float(percentageAmount) + float(delivery_charge)) 
        rocket_total = math.ceil(float(cartTotal) + float(cartTotal * 0.02) - float(order.cupon_amount) - float(percentageAmount) + float(delivery_charge)) 
        if request.method == 'POST' and 'method' in request.POST: 
            method = request.POST.get('method')
            if method == 'bkash':
                order.method = 'bkash'
                order.total = float(bkash_total)
            elif method == 'nagad':
                order.method = 'nagad'
                order.total = float(nagad_total) 
            elif method == 'rocket':
                order.method = 'rocket'
                order.total = float(rocket_total) 
            if method == 'cod':
                order.method = 'cod'
                order.total = float(cartTotal) - float(order.cupon_amount) + float(delivery_charge) - float(percentageAmount)


            order.due = float(order.total) - float(order.advance)
            order.save()
            return redirect('noksha:checkout')
        
        if request.method == 'POST' and 'order_confirm' in request.POST: 
            order.status = 'Customer Confirmed'
            order.address = shipping.address
            order.city = shipping.city
            order.member_amount = percentageAmount
            order.state = shipping.state
            order.delivery_fee = delivery_charge
            order.complete = True
            order.save()
            messages.success(request,'Order completed! you can track order from dashboard!')
            return redirect('noksha:home')

        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.image = ProductImages.objects.filter(product = product)[:1]
        
            
            context = {
                'member':member,
                'percentageAmount':percentageAmount,
                'items':items,
                'order':order,
                'nvCategorys':navbarCategorys,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'shipping':shipping,
                'bkash_total':bkash_total,
                'nagad_total':nagad_total,
                'rocket_total':rocket_total,
                'item.image':item.image,
                'delivery_charge':delivery_charge
            }
        else:
            context = {
                'percentageAmount':percentageAmount,
                'member':member,
                'items':items,
                'order':order,
                'cartItems':cartItems,
                'nvCategorys':navbarCategorys,
                'cartTotal':cartTotal,
                'shipping':shipping,
                'bkash_total':bkash_total,
                'nagad_total':nagad_total,
                'rocket_total':rocket_total,
                'delivery_charge':delivery_charge
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        if request.method =='POST' and 'login_username' in request.POST:
            login_username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            user_1 = User.objects.get(username = login_username)
            username = user_1.username

            user = authenticate(request,username=username, password=password)
            print(user)
            if user is not None:
                customer = Customer.objects.get(phone = login_username)
                shipping = ShippingAddress.objects.get(customer = customer)
                db_order,created = Order.objects.get_or_create(customer=customer, complete=False)
                db_order.cupon_code = order['cupon_code']
                db_order.cupon_amount = order['cupon_amount']
                db_order.address = shipping.address
                db_order.city = shipping.city
                db_order.state = shipping.state
                db_order.save()
                for item in items:
                    product = Product.objects.get(id=item['product']['id'])
                    quantity = item['quantity']
                    rate = product.price
                    total = float(product.price) * float(quantity)
                    orderItem, created  = OrderItem.objects.get_or_create(
                        product=product,
                        order = db_order,
                        customer=customer, 
                        )
                    orderItem.quantity=item['quantity']
                    orderItem.size = item['size']
                    orderItem.color = item['color']
                    orderItem.rate = rate
                    orderItem.total = total
                    orderItem.save()
                login(request,user)
                messages.success(request,'Login Successfull!')
                return redirect('noksha:checkout')
                

        if request.method =='POST' and 'reg_name' in request.POST:
            name =  request.POST.get('reg_name')
            email =  request.POST.get('reg_email')
            phone =  request.POST.get('reg_phone')
            reg_subscribe =  request.POST.get('reg_subscribe')
            address =  request.POST.get('address')
            area =  request.POST.get('area')
            city =  request.POST.get('city')
            if User.objects.filter(email=email).first():
                messages.error(request, 'Email is taken.')
                return redirect('noksha:checkout')
            elif Customer.objects.filter(phone = phone).first():
                messages.error(request, 'Phone is used on another account.')
                return redirect('noksha:checkout')
            else:
                user = User.objects.create(first_name = name, email=email,username=phone)
                user.set_password(phone[-6:])
                user.save()
                customer = Customer.objects.create(
                        user = user,
                        phone = phone,
                )
                if reg_subscribe == 'Yes':
                    member = Subscription.objects.create(email = email)
                shipping =  ShippingAddress.objects.create(
                    customer = customer,
                    address = address,
                    state = area,
                    city = city
                )
                group = Group.objects.get(name = 'customer')
                user.groups.add(group)
                if user is not None:
                    db_order,created = Order.objects.get_or_create(customer=customer, complete=False)
                    db_order.address = shipping.address
                    db_order.state = shipping.state
                    db_order.city = shipping.city
                    db_order.save()
                    for item in items:
                        product = Product.objects.get(id=item['product']['id'])
                        quantity = item['quantity']
                        rate = product.price
                        total = float(product.price) * float(quantity)
                        orderItem, created  = OrderItem.objects.get_or_create(
                            product=product,
                            order = db_order,
                            customer=customer
                        )
                        orderItem.quantity=item['quantity']
                        orderItem.size = item['size']
                        orderItem.color = item['color']
                        orderItem.rate = rate
                        orderItem.total = total
                        orderItem.save()
                    login(request,user)
                    return redirect('noksha:checkout')
                    
            messages.success(request,'SignuP Successfull!')
        bkash_total = math.ceil(float(cartTotal) + float(cartTotal * 0.02) - float(order['cupon_amount']))
        nagad_total = math.ceil(float(cartTotal) + float(cartTotal * 0.01494) - float(order['cupon_amount']))
        rocket_total = math.ceil(float(cartTotal) + float(cartTotal * 0.02) - float(order['cupon_amount'])) 
        
        total_items = len(items)
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id=item['product']['id'])
                item['image'] = ProductImages.objects.filter(product = product)[:1]
        

            context = {
                'percentageAmount':percentageAmount,
                'member':member,
                'items':items,
                'order':order,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'shipping':shipping,
                'nvCategorys':navbarCategorys,
                'bkash_total':bkash_total,
                'nagad_total':nagad_total,
                'rocket_total':rocket_total,
                'item.image':item['image'],
                'delivery_charge':delivery_charge
            }
        else:
            context = {
                'percentageAmount':percentageAmount,
                'member':member,
                'items':items,
                'order':order,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'nvCategorys':navbarCategorys,
                'shipping':shipping,
                'bkash_total':bkash_total,
                'nagad_total':nagad_total,
                'rocket_total':rocket_total,
                'delivery_charge':delivery_charge
            }
    return render(request,'store/pages/checkout.html',context)

def categoryView(request,pk):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Neccesary items
    all_categorys = []
    all_category_object = Category.objects.all()
    for i in all_category_object:
        all_categorys.append(categorywithSub(i.id))
    
    #Category Section
    selectedCategory = Category.objects.get(id=pk)
    subcategorys = SubCategory.objects.filter(category = selectedCategory)



    
     #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'subcategorys':subcategorys,
                'all_categorys':all_categorys,
                'nvCategorys':navbarCategorys,
                'selectedCategory':selectedCategory,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'subcategorys':subcategorys,
                'all_categorys':all_categorys,
                'nvCategorys':navbarCategorys,
                'selectedCategory':selectedCategory,
                'cartItems':cartItems,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        total_items = len(items)

        if total_items > 0:

            for item in items:
                product = Product.objects.get(id = item['product']['id'])
                item['sizes'] = product.size.all()
                item['colors'] = product.color.all()
                item['image'] = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'subcategorys':subcategorys,
                'all_categorys':all_categorys,
                'nvCategorys':navbarCategorys,
                'selectedCategory':selectedCategory,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item['image'],
                'item.sizes':item['sizes'],
                'item.colors':item['colors'],
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'subcategorys':subcategorys,
                'all_categorys':all_categorys,
                'nvCategorys':navbarCategorys,
                'selectedCategory':selectedCategory,
                'cartItems':cartItems,
            }
    return render(request,'store/pages/categoryview.html',context)

def subcategoryView(request,pk):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Neccesary items
    start_price = 200
    end_price = 3000
    sort_name = 'default'
    necessaryItems = {
        'sort_details': sort_name,
        'pricedetails':{
            'start_price': start_price,
            'end_price' : end_price
        },
    }
    all_categorys = []
    all_category_object = Category.objects.all()
    for i in all_category_object:
        all_categorys.append(categorywithSub(i.id))
    
    #Category Section
    selectedCategory = SubCategory.objects.get(id=pk)
    products = Product.objects.filter(subcategory = selectedCategory)
    if request.method == 'POST' and 'sort-details' in request.POST:
        sort_details = request.POST.get('sort-details')
        necessaryItems['sort_details'] = sort_details
        if sort_details == 'default':
            products = products
        elif sort_details == 'name_a_z':
            products = Product.objects.filter(subcategory = selectedCategory).order_by('name')
        elif sort_details == 'name_z_a':
            products = Product.objects.filter(subcategory = selectedCategory).order_by('-name')
        elif sort_details == 'price_l_h':
            products = Product.objects.filter(subcategory = selectedCategory).order_by('price')
        elif sort_details == 'price_h_l':
            products = Product.objects.filter(subcategory = selectedCategory).order_by('-price')
        elif sort_details == 'rate_h_l':
            products = Product.objects.filter(subcategory = selectedCategory).order_by('-rate')
        elif sort_details == 'rate_l_h':
            products = Product.objects.filter(subcategory = selectedCategory).order_by('rate')
            
        start_price =  request.POST.get('start_price')
        end_price =  request.POST.get('end_price')
        priceProducts = products.filter(subcategory = selectedCategory , price__gte =  start_price, price__lte = end_price)
        products = priceProducts
        necessaryItems['pricedetails']['start_price'] = start_price
        necessaryItems['pricedetails']['end_price'] = end_price

    categoryWithDetailedProduct = []
    allCategorys = Category.objects.all()
    for i in allCategorys:
        categoryWithDetailedProduct.append(category_with_products(i.id))

    outputProduct = []
    for k in products:
        outputProduct.append(productSerialize(k.id))
    

     #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'nvCategorys':navbarCategorys,
                'all_categorys':all_categorys,
                'selectedCategory':selectedCategory,
                'categoryWithDetailedProduct':categoryWithDetailedProduct,
                'necessaryItems':necessaryItems,
                'products':outputProduct,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'nvCategorys':navbarCategorys,
                'all_categorys':all_categorys,
                'selectedCategory':selectedCategory,
                'categoryWithDetailedProduct':categoryWithDetailedProduct,
                'necessaryItems':necessaryItems,
                'products':outputProduct,
                'cartItems':cartItems,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        total_items = len(items)

        if total_items > 0:

            for item in items:
                product = Product.objects.get(id = item['product']['id'])
                item['sizes'] = product.size.all()
                item['colors'] = product.color.all()
                item['image'] = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'nvCategorys':navbarCategorys,
                'selectedCategory':selectedCategory,
                'all_categorys':all_categorys,
                'categoryWithDetailedProduct':categoryWithDetailedProduct,
                'necessaryItems':necessaryItems,
                'products':outputProduct,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item['image'],
                'item.sizes':item['sizes'],
                'item.colors':item['colors'],
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'nvCategorys':navbarCategorys,
                'selectedCategory':selectedCategory,
                'all_categorys':all_categorys,
                'categoryWithDetailedProduct':categoryWithDetailedProduct,
                'necessaryItems':necessaryItems,
                'products':outputProduct,
                'cartItems':cartItems,
            }
    return render(request,'store/pages/subcategoryview.html',context)

def searchProduct(request,*arg,**kwargs):
    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Neccesary items
    start_price = 200
    end_price = 3000
    sort_name = 'default'
    necessaryItems = {
        'sort_details': sort_name,
        'pricedetails':{
            'start_price': start_price,
            'end_price' : end_price
        },
    }

    query = kwargs.pop('searchtext')
    products = Product.objects.filter(Q(name__icontains=query))
    

    if request.method == 'POST' and 'search' in request.POST:
        queryText = request.POST.get('search')
        category_id = request.POST.get('category_id')
        description = request.POST.get('description')

        if description is None:
            c_products = Product.objects.filter(category = category_id)
            products = c_products.filter(Q(name__icontains=queryText))
        else:
            c_products = Product.objects.filter(category = category_id)
            products = c_products.filter(Q(name__icontains=queryText) | Q(description__icontains=queryText))
    
    if request.method == 'POST' and 'sort-details' in request.POST:
        sort_details = request.POST.get('sort-details')
        necessaryItems['sort_details'] = sort_details
        if sort_details == 'default':
            products = products
        elif sort_details == 'name_a_z':
            products = products.order_by('name')
        elif sort_details == 'name_z_a':
            products = products.order_by('-name')
        elif sort_details == 'price_l_h':
            products = products.order_by('price')
        elif sort_details == 'price_h_l':
            products = products.order_by('-price')
        elif sort_details == 'rate_h_l':
            products = products.order_by('-rate')
        elif sort_details == 'rate_l_h':
            products = products.order_by('rate')
            
        start_price =  request.POST.get('start_price')
        end_price =  request.POST.get('end_price')
        priceProducts = products.filter(price__gte =  start_price, price__lte = end_price)
        products = priceProducts
        necessaryItems['pricedetails']['start_price'] = start_price
        necessaryItems['pricedetails']['end_price'] = end_price


    outputProduct = []
    for k in products:
        outputProduct.append(productSerialize(k.id))

    categorys = Category.objects.all()

    #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'nvCategorys':navbarCategorys,
                'products':outputProduct,
                'searchText':query,
                'categorys':categorys,
                'necessaryItems':necessaryItems,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'nvCategorys':navbarCategorys,
                'products':outputProduct,
                'searchText':query,
                'categorys':categorys,
                'necessaryItems':necessaryItems,
                'cartItems':cartItems,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        total_items = len(items)

        if total_items > 0:

            for item in items:
                product = Product.objects.get(id = item['product']['id'])
                item['sizes'] = product.size.all()
                item['colors'] = product.color.all()
                item['image'] = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                
                'nvCategorys':navbarCategorys,
                'products':outputProduct,
                'searchText':query,
                'categorys':categorys,
                'necessaryItems':necessaryItems,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item['image'],
                'item.sizes':item['sizes'],
                'item.colors':item['colors'],
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'nvCategorys':navbarCategorys,
                'products':outputProduct,
                'searchText':query,
                'categorys':categorys,
                'necessaryItems':necessaryItems,
                'cartItems':cartItems,
            }

    return render(request,'store/searchProduct.html',context)

def blog(request,pk):
    blog = blogs_with_detailed_date(pk)

    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'blog':blog,
                'nvCategorys':navbarCategorys,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'blog':blog,
                'nvCategorys':navbarCategorys,
                'cartItems':cartItems,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        total_items = len(items)

        if total_items > 0:

            for item in items:
                product = Product.objects.get(id = item['product']['id'])
                item['sizes'] = product.size.all()
                item['colors'] = product.color.all()
                item['image'] = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                
                'blog':blog,
                'nvCategorys':navbarCategorys,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item['image'],
                'item.sizes':item['sizes'],
                'item.colors':item['colors'],
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'blog':blog,
                'nvCategorys':navbarCategorys,
                'cartItems':cartItems,
            }
    return render(request,'store/blog.html',context)

def blogs(request):
    #Blogs Section
    blogs = []
    tmp_blogs = Blog.objects.all().order_by('-date_added')
    for i in tmp_blogs:
        blogs.append(blogs_with_detailed_date(i.id))

    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'blogs':blogs,
                'nvCategorys':navbarCategorys,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'blogs':blogs,
                'nvCategorys':navbarCategorys,
                'cartItems':cartItems,
            }

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        cartTotal = cookieData['cartTotal']
        order = cookieData['order']
        items = cookieData['items']
        total_items = len(items)

        if total_items > 0:

            for item in items:
                product = Product.objects.get(id = item['product']['id'])
                item['sizes'] = product.size.all()
                item['colors'] = product.color.all()
                item['image'] = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                
                'blogs':blogs,
                'nvCategorys':navbarCategorys,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item['image'],
                'item.sizes':item['sizes'],
                'item.colors':item['colors'],
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'blogs':blogs,
                'nvCategorys':navbarCategorys,
                'cartItems':cartItems,
            }
    return render(request,'store/blogs.html',context)


@login_required(login_url='noksha:login')
def view_order(request,pk):
    user_order = Order.objects.get(id = pk)
    user_order_items = OrderItem.objects.filter(order=user_order)

    #Navbar Section
    navbarCategoryObject =  IndivitualCategory.objects.get(category_for = 'nvcategory')
    navbarCategorys = navbarCategoryObject.categorys.all()

    #Cart Item Section
    delivery_charge_object = Delivery_charge.objects.get(w_delivery= 'Dhaka')
    delivery_charge = delivery_charge_object.fee
    price_total = 0
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.get_cart_items
        cartTotal = order.get_cart_total
        items = order.orderitem_set.all()
        total_items = items.count()
        if total_items> 0:
            for item in items:
                product = Product.objects.get(id = item.product.id)
                item.sizes = product.size.all()
                item.colors = product.color.all()
                item.image = ProductImages.objects.filter(product = product)[:1]
                price_total += product.price
        
            total = float(price_total) + float(delivery_charge)
            context = {
                'viewOrder': user_order,
                'viewItems': user_order_items,
                'viewNeed':order_with_discount_details(pk),
                'nvCategorys':navbarCategorys,
                'items':items,
                'cartItems':cartItems,
                'cartTotal':cartTotal,
                'order':order,
                'item.image':item.image,
                'item.sizes':item.sizes,
                'item.colors':item.colors,
                'delivery_charge':delivery_charge,
                'total':total,
            }
        else:
            context = {
                'viewOrder': user_order,
                'viewItems': user_order_items,
                'viewNeed':order_with_discount_details(pk),
                'nvCategorys':navbarCategorys,
                'cartItems':cartItems,
            }
    return render(request,'store/viewOrder.html',context)

decorators = [shopowner_only,allowed_users(allowed_roles=['admin']),login_required(login_url='noksha:login')]
@method_decorator(decorators, name='dispatch')
class shopDashboard(View):

    def get(self,request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            orders = []
            tmp_orders = Order.objects.filter(complete = True).order_by('-date_created')
            
            #Status Section 
            total_orders = tmp_orders.count()
            delivered = tmp_orders.filter(status = 'Delivered').count()
            transit = tmp_orders.filter(status = 'In-Transit').count()
            confirmed = tmp_orders.filter(status = 'Admin Confirmed').count()
            pending = tmp_orders.filter(status = 'Customer Confirmed').count()
            returns = tmp_orders.filter(status = 'Return').count()
            cancel = tmp_orders.filter(status = 'Cancel').count()

            status = {
                'total_orders':total_orders,
                'delivered':delivered,
                'transit':transit,
                'confirmed':confirmed, 
                'pending':pending,
                'return':returns,
                'cancel':cancel
            }

            for i in tmp_orders:
                orders.append(orderFetch(i.id))
            return JsonResponse({'orders':orders,'status':status})
        context = {}
        return render(request,'shop/pages/shopDashboard.html',context)

@shopowner_only
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='noksha:login')
def updateOrder(request,pk):
    user_order = Order.objects.get(id = pk)
    user_order_items = OrderItem.objects.filter(order=user_order)
    if request.method ==  'POST' and 'status' in request.POST:
        status = request.POST.get('status')
        user_order.status = status
        user_order.save()
        messages.success(request,'Status updated!')
        return redirect(reverse('noksha:update-order', kwargs={'pk':pk}))

    if request.method ==  'POST' and 'amount' in request.POST:
        amount = request.POST.get('amount')
        user_order.advance += float(amount)
        user_order.due = float(user_order.total) - float(user_order.advance)
        user_order.save()
        messages.success(request,'Amount added!')
        return redirect(reverse('noksha:update-order', kwargs={'pk':pk}))

    context = {
        'viewOrder': user_order,
        'viewItems': user_order_items,
        'viewNeed':order_with_discount_details(pk),
        }
    return render(request,'shop/pages/updateOrder.html',context)

@shopowner_only
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='noksha:login')
def products(request):
    products = []
    tmp_products = Product.objects.all().order_by('-date_created')
    for i in tmp_products:
        products.append(productSerialize(i.id))

    product_categorys = Category.objects.all().order_by('name')
    product_sizes = Size.objects.all().order_by('size')
    product_colors = Color.objects.all().order_by('color')

    #Add Product Section
    if request.method == 'POST' and 'product_name' in request.POST:
        name = request.POST.get('product_name')
        price = request.POST.get('product_price')
        code = request.POST.get('product_code')
        stock = request.POST.get('product_stock')
        description = request.POST.get('product_description')
        categorys = request.POST.getlist('product_categorys')
        sizes = request.POST.getlist('product_sizes')
        colors = request.POST.getlist('product_colors')
        image = request.FILES.get('product_image')
        zoom_image = request.FILES.get('product_image2')
        new_product = Product.objects.create(
            name = name,
            price = price,
            product_code = code,
            stock = stock,
            description = description,
        )
        for category in categorys:
            new_product.category.add(category)
        
        for size in sizes:
            new_product.size.add(size)
        
        for color in colors:
            new_product.color.add(color)

        prodduct_img = ProductImages.objects.create(
            product = new_product,
            n_img = image,
            Z_img = zoom_image
        )
        messages.success(request,'Product added successfully!')
        return redirect('noksha:products')
    
    #Delete Product Section
    if request.method == 'POST' and 'product_delete' in request.POST:
        id = request.POST.get('product_delete')
        delete_product = Product.objects.get(id = id)
        images_of_delete_products = ProductImages.objects.filter(product = delete_product)
        for i in images_of_delete_products:
            i.delete()
        delete_product.delete()
        messages.success(request,'Product deleted successfully!')
        return redirect('noksha:products')

    #Add Category Section
    if request.method == 'POST' and 'category_name' in request.POST:
        category_name = request.POST.get('category_name')
        new_category = Category.objects.create(name=category_name)
        messages.success(request,'Category added successfully!')
        return redirect('noksha:products')
    
    #Delete Category Section
    if request.method == 'POST' and 'category_delete' in request.POST:
        id = request.POST.get('category_delete')
        delete_category = Category.objects.get(id = id)
        delete_category.delete()
        messages.success(request,'Category deleted successfully!')
        return redirect('noksha:products')
    
     #Add Color Section
    if request.method == 'POST' and 'color_name' in request.POST:
        color_name = request.POST.get('color_name')
        new_color = Color.objects.create(color=color_name)
        messages.success(request,'Color added successfully!')
        return redirect('noksha:products')
    
    #Delete Color Section
    if request.method == 'POST' and 'color_delete' in request.POST:
        id = request.POST.get('color_delete')
        delete_color = Color.objects.get(id = id)
        delete_color.delete()
        messages.success(request,'Color deleted successfully!')
        return redirect('noksha:products')

    #Add Size Section
    if request.method == 'POST' and 'size_name' in request.POST:
        size_name = request.POST.get('size_name')
        new_size = Size.objects.create(size=size_name)
        messages.success(request,'Size added successfully!')
        return redirect('noksha:products')
    
    #Delete Size Section
    if request.method == 'POST' and 'size_delete' in request.POST:
        id = request.POST.get('size_delete')
        delete_size = Size.objects.get(id = id)
        delete_size.delete()
        messages.success(request,'Size deleted successfully!')
        return redirect('noksha:products')

    context = {
        'products':products,
        'categorys':product_categorys,
        'sizes':product_sizes,
        'colors':product_colors,
    }
    return render(request,'shop/pages/products.html',context)

@shopowner_only
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='noksha:login')
def shopProductView(request,pk):
    #Product Section
    product = Product.objects.get(id=pk)
    images = ProductImages.objects.filter(product=product)
    big_img = ProductImages.objects.filter(product=product)[:1]
    product_categorys = Category.objects.all().order_by('name')
    product_sizes = Size.objects.all().order_by('size')
    product_colors = Color.objects.all().order_by('color')

    #Update Product Section
    form = ProductForm(instance=product)
    if request.method == "POST" and 'name' in request.POST:
        stock = request.POST.get('edit_product_stock')
        form = ProductForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
            product.stock += int(stock)
            product.save()
            messages.success(request,'Product updated successfully!')
            return redirect(reverse('noksha:shop_product_view', kwargs={'pk':pk}))
        else:
            print(form.errors)
            form = ProductForm(instance=product)
    
    #Delete Product Section
    if request.method == 'POST' and 'product_delete' in request.POST:
        id = request.POST.get('product_delete')
        delete_product = Product.objects.get(id = id)
        images_of_delete_products = ProductImages.objects.filter(product = delete_product)
        for i in images_of_delete_products:
            i.delete()
        delete_product.delete()
        messages.success(request,'Product deleted successfully!')
        return redirect(reverse('noksha:shop_product_view', kwargs={'pk':pk}))
    
    #Delete Review Section
    if request.method == 'POST' and 'review_delete' in request.POST:
        id = request.POST.get('review_delete')
        delete_review = Review.objects.get(id = id)
        images_of_delete_review = ReviewImages.objects.filter(review = delete_review)
        for i in images_of_delete_review:
            i.delete()
        delete_review.delete()
        messages.success(request,'Review deleted successfully!')
        return redirect(reverse('noksha:shop_product_view', kwargs={'pk':pk}))

    #Upload Image Section
    if request.method == 'POST' and 'product_id' in request.POST:
        product_id = request.POST.get('product_id')
        image = request.FILES.get('product_image')
        zoom_image = request.FILES.get('product_image2')
        print(product_id)
        img_product = Product.objects.get(id = product_id)
        new_images = ProductImages.objects.create(product = img_product)
        new_images.n_img = image
        new_images.Z_img = zoom_image
        new_images.save()
        messages.success(request,'Image added successfully!')
        return redirect(reverse('noksha:shop_product_view', kwargs={'pk':pk}))

    #Delete Image Section
    if request.method == 'POST' and 'image_delete' in request.POST:
        id = request.POST.get('image_delete')
        delete_image = ProductImages.objects.get(id = id)
        delete_image.delete()
        messages.success(request,'Image deleted successfully!')
        return redirect(reverse('noksha:shop_product_view', kwargs={'pk':pk}))

    #Review Section
    reviews = []
    tmp_reviews = Review.objects.filter(product=product)
    total_review = tmp_reviews.count()
    review_count = 0
    for i in tmp_reviews:
        reviews.append(reviews_with_images(i.id))
        review_count += i.rate
        product.rate = float(review_count/total_review)
        product.save()

    

    context={
        'product':product,
        'images':images,
        'big_img':big_img,
        'total_review':total_review,
        'reviews':reviews,
        'categorys':product_categorys,
        'sizes':product_sizes,
        'colors':product_colors,
        'form':form
    }
    return render(request,'shop/pages/productView.html',context)

@shopowner_only
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='noksha:login')
def storeSettings(request):
    #Neccesary Items
    categorys = Category.objects.all()
    subcategorys = SubCategory.objects.all()

    #Banner Section
    homebannerItems = HomeBannerCategory.objects.all()[:3]
    total_home_banner_items = homebannerItems.count()

    #Upload Home Banner
    if request.method == 'POST' and 'title_heading' in request.POST:
        title_heading = request.POST.get('title_heading')
        estimated_category = request.POST.get('estimated_category')
        banner_img = request.FILES.get('banner_img')
        added_category = Category.objects.get(id = estimated_category)
        if HomeBannerCategory.objects.filter(estimated_category = added_category).exists():
            messages.error(request,'Category already in use!')
            return redirect('noksha:store_setting')
        else:
            new_home_banner =  HomeBannerCategory.objects.create(estimated_category = added_category)
            new_home_banner.title_heading = title_heading
            new_home_banner.banner_img = banner_img
            new_home_banner.save()
            messages.success(request,'Banner created successfully!')
            return redirect('noksha:store_setting')

    #Update Home Banner
    if request.method == "POST" and 'banner_id' in request.POST:
        banner_id = request.POST.get('banner_id')
        update_banner_title = request.POST.get('update_banner_title')
        update_banner_subheading = request.POST.get('update_banner_subheading')
        update_short_description = request.POST.get('update_short_description')
        update_estimated_category = request.POST.get('update_estimated_category')
        update_banner_img = request.FILES.get('update_banner_img')
        update_home_banner_object = HomeBannerCategory.objects.get(id = banner_id)
        update_home_banner_object.title_heading = update_banner_title
        update_home_banner_object.sub_title_heading = update_banner_subheading
        update_home_banner_object.short_description = update_short_description
        update_new_category = Category.objects.get(id = update_estimated_category)
        update_home_banner_object.estimated_category = update_new_category
        if update_banner_img:
            update_home_banner_object.banner_img = update_banner_img
        update_home_banner_object.save()
        messages.success(request,'Banner updated successfully!')
        return redirect('noksha:store_setting')
    
    #Delete Home Banner
    if request.method == 'POST' and 'home_banner_delete' in request.POST:
        id =  request.POST.get('home_banner_delete')
        delete_banner_object =  HomeBannerCategory.objects.get(id = id)
        delete_banner_object.delete()
        messages.success(request,'Banner deleted successfully!')
        return redirect('noksha:store_setting')

    #Collection 
    collectionItems = CollectionCategory.objects.all()
    total_collection_items = collectionItems.count()

    #Upload Collection
    if request.method == 'POST' and 'estimated_category_collection' in request.POST:
        up_estimated_category = request.POST.get('estimated_category_collection')
        img = request.FILES.get('img')
        added_category = Category.objects.get(id = up_estimated_category)
        if CollectionCategory.objects.filter(estimated_category = added_category).exists():
            messages.error(request,'Category already in use!')
            return redirect('noksha:store_setting')
        else:
            new_collection =  CollectionCategory.objects.create(estimated_category = added_category)
            new_collection.img = img
            new_collection.save()
            messages.success(request,'Collection created successfully!')
            return redirect('noksha:store_setting')

    #Update Collection
    if request.method == 'POST' and 'collection_id' in request.POST:
        collection_id = request.POST.get('collection_id')
        update_collection_estimated_category = request.POST.get('update_collection_estimated_category')
        update_collection_img = request.FILES.get('update_collection_img')
        update_collection_object = CollectionCategory.objects.get(id = collection_id)
        update_new_category_collection = Category.objects.get(id = update_collection_estimated_category)
        update_collection_object.estimated_category = update_new_category_collection
        if update_collection_img:
            update_collection_object.img = update_collection_img
        update_collection_object.save()

        messages.success(request,'Collection updated successfully!')
        return redirect('noksha:store_setting')
    
    
    #Delete Collection
    if request.method == 'POST' and 'collection_delete' in request.POST:
        id =  request.POST.get('collection_delete')
        delete_collection_object =  CollectionCategory.objects.get(id = id)
        delete_collection_object.delete()
        messages.success(request,'Collection deleted successfully!')
        return redirect('noksha:store_setting')

    #ShopNow Category
    shopnowItems = ShopNowCategorys.objects.all()
    total_shopnow_items = shopnowItems.count()

    #Upload ShopNow Category
    if request.method == 'POST' and 'estimated_category_shop' in request.POST:
        sn_estimated_category = request.POST.get('estimated_category_shop')
        up_img = request.FILES.get('img')
        added_category = SubCategory.objects.get(id = sn_estimated_category)
        if ShopNowCategorys.objects.filter(estimated_category = added_category).exists():
            messages.error(request,'Category already in use!')
            return redirect('noksha:store_setting')
        else:
            new_shopnow =  ShopNowCategorys.objects.create(estimated_category = added_category)
            new_shopnow.img = up_img
            new_shopnow.save()
            messages.success(request,'Banner created successfully!')
            return redirect('noksha:store_setting')

     #Update ShopNow Category
    if request.method == 'POST' and 'shopnow_id' in request.POST:
        shopnow_id = request.POST.get('shopnow_id')
        update_shopnow_estimated_category = request.POST.get('update_shopnow_estimated_category')
        update_shopnow_img = request.FILES.get('update_shopnow_img')
        update_shopnow_object = ShopNowCategorys.objects.get(id = shopnow_id)
        update_new_category_shopnow = SubCategory.objects.get(id = update_shopnow_estimated_category)
        update_shopnow_object.estimated_category = update_new_category_shopnow
        if update_shopnow_img:
            update_shopnow_object.img = update_shopnow_img
        update_shopnow_object.save()

        messages.success(request,'Shop Now Category updated successfully!')
        return redirect('noksha:store_setting')

    #Delete ShopNow Category
    if request.method == 'POST' and 'shopnow_delete' in request.POST:
        id =  request.POST.get('shopnow_delete')
        delete_shopnow_object =  ShopNowCategorys.objects.get(id = id)
        delete_shopnow_object.delete()
        messages.success(request,'Shop Now Category deleted successfully!')
        return redirect('noksha:store_setting')

    
    #Latest Arrivals
    ltproducts = []
    lt_object =  LatestArrivals.objects.get(products_for = 'latestarrivals')
    for i in lt_object.products.all():
        ltproducts.append(productSerialize(i.id))
    
    products = []
    tmp_products = Product.objects.all().order_by('-date_created')
    for i in tmp_products:
        if i in lt_object.products.all():
            pass
        else:
            products.append(productSerialize(i.id))
    
    #Add Products To Latest Arrivals
    if request.method == 'POST' and 'products_id_list' in request.POST:
        products_id_list = request.POST.getlist('products_id_list')
        for i in products_id_list:
            add_product = Product.objects.get(id = i)
            lt_object.products.add(add_product)

        messages.success(request,'Product added to latest arrivals!')
        return redirect('noksha:store_setting')

    #Remove Products From Latest Arrivals
    if request.method == 'POST' and 'latest_delete' in request.POST:
        id =  request.POST.get('latest_delete')
        remove_product = Product.objects.get(id = id)
        lt_object.products.remove(remove_product)
        messages.success(request,'Product removed from latest arrivals!')
        return redirect('noksha:store_setting')

    
    #Indivitual Category Section
    nvCategorys = IndivitualCategory.objects.get(category_for = 'nvcategory')
    total_nvCategorys = nvCategorys.categorys.all().count()

    mvCategorys = PopularFurniture.objects.get(category_for = 'pvfurniture')
    total_mvCategorys = mvCategorys.categorys.all().count()

    #Add Category
    if request.method == 'POST' and 'category_id_list' in request.POST:
        add_category_for_indivitual = request.POST.get('add_category_for_indivitual')
        if add_category_for_indivitual == 'nvcategory':
            category_id_list = request.POST.getlist('category_id_list')
            add_category_for = IndivitualCategory.objects.get(category_for = add_category_for_indivitual)
            for i in category_id_list:
                to_be_add_category = Category.objects.get(id = i)
                add_category_for.categorys.add(to_be_add_category)

        
        elif add_category_for_indivitual == 'pvfurniture':
            category_id_list = request.POST.getlist('category_id_list')
            add_category_for = PopularFurniture.objects.get(category_for = add_category_for_indivitual)
            for i in category_id_list:
                to_be_add_category = SubCategory.objects.get(id = i)
                add_category_for.categorys.add(to_be_add_category)

        messages.success(request,'Categorys added to indivitual categorys!')
        return redirect('noksha:store_setting')

    #Remove Category
    if request.method == 'POST' and 'category_for_indivitual' in request.POST:
        category_for_indivitual = request.POST.get('category_for_indivitual')

        if category_for_indivitual == 'nvcategory':
            category_remove = request.POST.get('category_remove')
            remove_category = Category.objects.get(id = category_remove)
            remove_category_indivitual = IndivitualCategory.objects.get(category_for = category_for_indivitual)
            remove_category_indivitual.categorys.remove(remove_category)
            
        elif category_for_indivitual == 'pvfurniture':
            category_remove = request.POST.get('category_remove')
            remove_category = SubCategory.objects.get(id = category_remove)
            remove_category_indivitual = PopularFurniture.objects.get(category_for = category_for_indivitual)
            remove_category_indivitual.categorys.remove(remove_category)

        messages.success(request,'Category removed from indivitual categorys!')
        return redirect('noksha:store_setting')


    context = {
        'homebannerItems':homebannerItems,
        'total_home_banner_items':total_home_banner_items,
        'collectionItems':collectionItems,
        'total_collection_items':total_collection_items,
        'shopnowItems':shopnowItems,
        'total_shopnow_items':total_shopnow_items,
        'ltproducts':ltproducts,
        'products':products,
        'categorys':categorys,
        'nvCategorys':nvCategorys,
        'total_nvCategorys':total_nvCategorys,
        'mvCategorys':mvCategorys,
        'total_mvCategorys':total_mvCategorys,
        'subcategorys':subcategorys
    }
    return render(request,'shop/pages/storeSetting.html',context)



def bannerSetting(request,pk):
    banner = HomeBannerCategory.objects.get(id = pk)
    category_id = banner.estimated_category.id
    category_name = banner.estimated_category.name

    context = {
        'id':banner.id,
        'title_heading':banner.title_heading,
        'category_id' :category_id,
        'estimated_category':category_name,
        'banner_img':banner.banner_img.url
    }
    return JsonResponse({'banner':context})

def collectionSetting(request,pk):
    collection = CollectionCategory.objects.get(id = pk)
    category_id = collection.estimated_category.id
    category_name = collection.estimated_category.name

    context = {
        'id':collection.id,
        'category_id' :category_id,
        'estimated_category':category_name,
        'img':collection.img.url
    }
    return JsonResponse({'collection':context})

def shopnowSetting(request,pk):
    shopnow = ShopNowCategorys.objects.get(id = pk)
    category_id = shopnow.estimated_category.id
    category_name = shopnow.estimated_category.name

    context = {
        'id':shopnow.id,
        'category_id' :category_id,
        'estimated_category':category_name,
        'img':shopnow.img.url
    }
    return JsonResponse({'shopnow':context})

@shopowner_only
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='noksha:login')
def createOrder(request):
    #Neccessary Items
    products = []
    tmp_products = Product.objects.all().order_by('-date_created')
    for i in tmp_products:
        products.append(productSerialize(i.id))
    sizes = Size.objects.all().order_by('size')
    colors = Color.objects.all().order_by('color')
    offileOrder, created = Order.objects.get_or_create(complete = False,transaction_id = 'offline-order',status = 'Admin Confirmed')
    offileItems = OrderItem.objects.filter(order = offileOrder)
    total_offlineItems = offileItems.count()
    viewNeed = order_with_discount_details(offileOrder.id)

    #Add Customer
    if request.method == 'POST' and 'phone' in request.POST:
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        area = request.POST.get('area')
        city = request.POST.get('city')
        if User.objects.filter(username = phone).exists():
            add_user = User.objects.get(username = phone)
            add_customer = Customer.objects.get(user = add_user)
            shipping = ShippingAddress.objects.get(customer = add_customer)

        elif Customer.objects.filter(phone = phone).exists():
            add_customer = Customer.objects.get(phone = phone)
            shipping = ShippingAddress.objects.get(customer = add_customer)
        
        else: 
            add_user = User.objects.create(username = phone)
            add_customer = Customer.objects.create(user = add_user)
            shipping = ShippingAddress.objects.create(customer = add_customer)
            add_user.email = email
            add_user.first_name = name
            add_user.set_password(phone[-6:])
            add_customer.phone = phone
            shipping.address = address
            shipping.state = area
            shipping.city = city
            add_user.save()
            add_customer.save()
            shipping.save()
        
        offileOrder.customer = add_customer
        offileOrder.address = shipping.address
        offileOrder.state = shipping.state
        offileOrder.city = shipping.city
        if offileOrder.city == 'Dhaka':
            delivery_fee_object = Delivery_charge.objects.get(w_delivery = 'Dhaka')
            delivery_fee = delivery_fee_object.fee
        else:
            delivery_fee_object = Delivery_charge.objects.get(w_delivery = 'Other')
            delivery_fee = delivery_fee_object.fee
        offileOrder.delivery_fee = delivery_fee
        offileOrder.total += offileOrder.delivery_fee
        offileOrder.save()
        messages.success(request,'Customer added to the order!')
        return redirect('noksha:create_order')


    #Add To Shopping Cart
    if request.method == 'POST' and 'product_id' in request.POST:
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        size = request.POST.get('size')
        color = request.POST.get('color')
        added_product = Product.objects.get(id = product_id)
        item_added ,created = OrderItem.objects.get_or_create(order = offileOrder, product = added_product)
        item_added.quantity += int(quantity)
        item_added.rate = math.ceil(float(added_product.price))
        item_added.total = math.ceil(float(added_product.price) * float(item_added.quantity))
        offileOrder.total += math.ceil(float(item_added.total))
        offileOrder.save()
        item_added.size = size
        item_added.color = color
        item_added.save()
        messages.success(request,'Product added to shopping cart!')
        return redirect('noksha:create_order')
    
    #Remove From Shopping Cart
    if request.method == 'POST' and 'remove-item' in request.POST:
        remove_item = request.POST.get('remove-item')
        item_object = OrderItem.objects.get(id = remove_item)
        offileOrder.total -= math.ceil(float(item_object.total))
        offileOrder.save()
        item_object.delete()
        messages.success(request,'Item removed from shopping cart!')
        return redirect('noksha:create_order')
    
    #Method & Paid:
    if request.method == 'POST' and 'payment_method' in request.POST:
        payment_method = request.POST.get('payment_method')
        paid_amount = request.POST.get('paid_amount')
        offileOrder.method = payment_method
        if offileOrder.method == 'bkash':
            charges = float(float(viewNeed['sub_total']) * 0.02)
        elif offileOrder.method == 'nagad':
            charges = float(float(viewNeed['sub_total']) * 0.01494)
        elif offileOrder.method == 'rocket':
            charges = float(float(viewNeed['sub_total']) * 0.02)
        else: 
            charges = 0
        offileOrder.total += math.ceil(charges)
        offileOrder.advance += math.ceil(float(paid_amount))
        offileOrder.due = math.ceil(offileOrder.total - offileOrder.advance)
        offileOrder.save()
        messages.success(request,'Method & Paid updated!')
        return redirect('noksha:create_order')

    #Confirm Order
    if request.method == 'POST' and 'confirm_order' in request.POST:
        offileOrder.complete = True
        offileOrder.save()
        messages.success(request,'Order completed!')
        return redirect('noksha:shop_dashboard')

    if total_offlineItems > 0:
        for item in offileItems:
            item.image = ProductImages.objects.filter(product = item.product)[:1]
        context = {
            'viewOrder':offileOrder,
            'viewItems':offileItems,
            'viewNeed':viewNeed,
            'products':products,
            'sizes':sizes,
            'colors':colors,
            'item.image':item.image,
            'total_items':total_offlineItems,
        }
    else:
        context = {
            'viewOrder':offileOrder,
            'viewItems':offileItems,
            'viewNeed':viewNeed,
            'products':products,
            'sizes':sizes,
            'colors':colors,
            'total_items':total_offlineItems,
        }
    return render(request,'shop/pages/createOrder.html',context)

def fetchCustomer(*arg,**kwargs):
    phone = kwargs.pop('phone')
    if User.objects.filter(username = phone).exists() or Customer.objects.filter(phone = phone).exists():
        user = User.objects.get(username = phone)
        customer = Customer.objects.get(user = user)
        shipping = ShippingAddress.objects.get(customer = customer)
        context = {
            'name' : user.first_name,
            'email' : user.email,
            'address' :shipping.address,
            'area':shipping.state,
            'city':shipping.city,
        }
    else:
        context = {
            'name' : '',
            'email' : '',
            'address' : '',
            'area': '',
            'city': '',
        }
    return JsonResponse({'customer':context})

@shopowner_only
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='noksha:login')
def controlPanel(request):
    #Neccessary Items
    discount_products = []
    tmp_products = Product.objects.all().order_by('-date_created')
    for i in tmp_products:
        if i.discount <= 0 :
            discount_products.append(productSerialize(i.id))
        else:
            pass


    #Customer Items
    customers = []
    tmp_customers = Customer.objects.all().order_by('-date_created')
    for i in tmp_customers:
        customers.append(customerControl(i.id))
    total_customers = tmp_customers.count()

    #Delivery Charge
    delivery_charge_objects = Delivery_charge.objects.all()[:2]
    if request.method == 'POST' and 'w_delivery' in request.POST:
        w_delivery = request.POST.get('w_delivery')
        fee = request.POST.get('fee')
        update_charge_object = Delivery_charge.objects.get(w_delivery = w_delivery)
        update_charge_object.fee = int(fee)
        update_charge_object.save()
        messages.success(request,'Delivery fee updated!')
        return redirect('noksha:control_panel')
    
    #Cupon Section
    cupon_objects  = Cupon.objects.all().order_by('cupon_code')

    #Add Coupon
    if request.method == "POST" and 'add_cupon_name' in request.POST:
        cupon_code = request.POST.get('add_cupon_name')
        amount = request.POST.get('add_cupon_amount')
        new_coupon_object =  Cupon.objects.create(cupon_code = cupon_code)
        new_coupon_object.amount = amount
        new_coupon_object.save()
        messages.success(request,'Cupon created successfully!')
        return redirect('noksha:control_panel')
    
    #Delete Coupon
    if request.method == 'POST'  and 'cupon_id' in request.POST:
        delete_coupon_object = Cupon.objects.get(id =  request.POST.get('cupon_id'))
        delete_coupon_object.delete()
        messages.success(request,'Cupon deleted successfully!')
        return redirect('noksha:control_panel')


    #Discount Section
    discounts = DiscountDetails.objects.all()

    #Add Discount
    if request.method == 'POST' and 'discount_name' in request.POST:
        discount_name = request.POST.get('discount_name')
        percentage = request.POST.get('percentage')
        discount_products = request.POST.getlist('products')
        new_discount_category = Category.objects.create(name = discount_name)
        new_discount_object = DiscountDetails.objects.create(category = new_discount_category)
        new_discount_object.name = discount_name
        new_discount_object.percentage = percentage
        for i in discount_products:
            added_product = Product.objects.get(id = i)
            added_product.discount = int(percentage)
            added_product.discount_amount = math.floor(float(added_product.price) * (float(percentage) / 100))
            added_product.price -= added_product.discount_amount
            added_product.category.add(new_discount_category)
            added_product.featured = True
            added_product.save()
            new_discount_object.products.add(added_product)
        new_discount_object.save()

        messages.success(request,'Discount created successfully!')
        return redirect('noksha:control_panel')
    
    #Add Products to Discount
    if request.method == 'POST' and 'add_product_list' in request.POST:
        add_product_list = request.POST.getlist('add_product_list')
        discount_object = DiscountDetails.objects.get(id = request.POST.get('discount_id'))
        for i in add_product_list:
            product_object = Product.objects.get(id = i)
            product_object.discount = int(discount_object.percentage)
            product_object.discount_amount = math.floor(float(product_object.price) * (float(discount_object.percentage) / 100))
            product_object.price -= product_object.discount_amount
            product_object.category.add(discount_object.category)
            product_object.featured = True
            product_object.save()
            discount_object.products.add(product_object)

        messages.success(request,'Products added to the discount!')
        return redirect('noksha:control_panel')
    
    #Remove Products from Discount
    if request.method == 'POST' and 'remove_product_list' in request.POST:
        remove_product_list = request.POST.getlist('remove_product_list')
        remove_discount_object = DiscountDetails.objects.get(id = request.POST.get('discount_id'))
        for i in remove_product_list:
            remove_product_object = Product.objects.get(id = i)
            remove_product_object.discount = 0
            remove_product_object.price += remove_product_object.discount_amount
            remove_product_object.discount_amount = 0
            remove_product_object.category.remove(remove_discount_object.category)
            remove_product_object.featured = False
            remove_product_object.save()
            remove_discount_object.products.remove(remove_product_object)

        messages.success(request,'Products removed from the discount!')
        return redirect('noksha:control_panel')
    
    #Delete Discountremove_category
    if request.method == 'POST' and 'remove_discount' in request.POST:
        delete_discount_object = DiscountDetails.objects.get(id = request.POST.get('remove_discount'))
        delete_category = delete_discount_object.category
        for i in delete_discount_object.products.all():
            delete_product_object = Product.objects.get(id = i.id)
            delete_product_object.discount = 0
            delete_product_object.price += delete_product_object.discount_amount
            delete_product_object.discount_amount = 0
            delete_product_object.category.remove(delete_discount_object.category)
            delete_product_object.featured = False
            delete_product_object.save()
            delete_discount_object.products.remove(delete_product_object)

        delete_discount_object.delete()
        delete_category.delete()

        messages.success(request,'Discount deleted successfully!')
        return redirect('noksha:control_panel')
    
    #Category Section
    category_products = Product.objects.all().order_by('name')
    categorys = []
    tmp_categorys = Category.objects.all().order_by('name')
    for i in tmp_categorys:
        name = i.name
        id = i.id
        hasProducts = Product.objects.filter(category = i).count()
        categoryProducts = Product.objects.filter(category = i)

        categoryWithProducts = {
        'id':id,
        'name':name,
        'hasProducts':hasProducts,
        'categoryProducts':categoryProducts
        }
        categorys.append(categoryWithProducts)
    
    #Add Category
    if request.method == 'POST' and 'add_category_name' in request.POST:
        add_category_name = request.POST.get('add_category_name')
        category_product_list = request.POST.getlist('category_product_list')
        total_category_products = len(category_product_list)
        new_category_object = Category.objects.create(name = add_category_name)
        if total_category_products > 0:
            for i in category_product_list:
                categoryProduct = Product.objects.get(id = i)
                categoryProduct.category.add(new_category_object)
        
        messages.success(request,'Category created successfully!')
        return redirect('noksha:control_panel')

    #Add Products To Category
    if request.method == 'POST' and 'category_add_product_list' in request.POST:
        category_add_product_list = request.POST.getlist('category_add_product_list')
        category_object = Category.objects.get(id = request.POST.get('category_id'))
        for i in category_add_product_list:
            category_add_product = Product.objects.get(id = i)
            category_add_product.category.add(category_object)

        messages.success(request,'Product added to category successfully!')
        return redirect('noksha:control_panel')
    
    #Remove Products From Category
    if request.method == 'POST' and 'category_remove_product_list' in request.POST:
        category_remove_product_list = request.POST.getlist('category_remove_product_list')
        category_remove_object = Category.objects.get(id = request.POST.get('category_id'))
        for i in category_remove_product_list:
            category_add_product = Product.objects.get(id = i)
            category_add_product.category.remove(category_remove_object)

        messages.success(request,'Product removed from category successfully!')
        return redirect('noksha:control_panel')

    #Delete Category 
    if request.method == 'POST' and 'remove_category' in request.POST:
        delete_category_object = Category.objects.get(id = request.POST.get('remove_category'))
        delete_category_object.delete()

        messages.success(request,'Category deleted successfully!')
        return redirect('noksha:control_panel')

    #Size Section
    sizes = []
    tmp_sizes = Size.objects.all().order_by('size')
    for i in tmp_sizes:
        size = i.size
        id = i.id
        hasProducts = Product.objects.filter(size = i).count()
        sizeProducts = Product.objects.filter(size = i)

        sizeWithProducts = {
        'id':id,
        'size':size,
        'hasProducts':hasProducts,
        'sizeProducts':sizeProducts
        }
        sizes.append(sizeWithProducts)

    #Add Size
    if request.method == 'POST' and 'add_size_name' in request.POST:
        add_size_name = request.POST.get('add_size_name')
        size_product_list = request.POST.getlist('size_product_list')
        total_size_products = len(size_product_list)
        new_size_object = Size.objects.create(size = add_size_name)
        if total_size_products > 0:
            for i in size_product_list:
                sizeProduct = Product.objects.get(id = i)
                sizeProduct.size.add(new_size_object)
        
        messages.success(request,'Size created successfully!')
        return redirect('noksha:control_panel')

    #Add Products To Size
    if request.method == 'POST' and 'size_add_product_list' in request.POST:
        size_add_product_list = request.POST.getlist('size_add_product_list')
        size_object = Size.objects.get(id = request.POST.get('size_id'))
        for i in size_add_product_list:
            size_add_product = Product.objects.get(id = i)
            size_add_product.size.add(size_object)

        messages.success(request,'Product added to size successfully!')
        return redirect('noksha:control_panel')
    
    #Remove Products From Size
    if request.method == 'POST' and 'size_remove_product_list' in request.POST:
        size_remove_product_list = request.POST.getlist('size_remove_product_list')
        size_remove_object = Size.objects.get(id = request.POST.get('size_id'))
        for i in size_remove_product_list:
            size_add_product = Product.objects.get(id = i)
            size_add_product.size.remove(size_remove_object)

        messages.success(request,'Product removed from size successfully!')
        return redirect('noksha:control_panel')

    #Delete Size 
    if request.method == 'POST' and 'remove_size' in request.POST:
        delete_size_object = Size.objects.get(id = request.POST.get('remove_size'))
        delete_size_object.delete()

        messages.success(request,'Size deleted successfully!')
        return redirect('noksha:control_panel')


#Color Section
    colors = []
    tmp_colors = Color.objects.all().order_by('color')
    for i in tmp_colors:
        color = i.color
        id = i.id
        hasProducts = Product.objects.filter(color = i).count()
        colorProducts = Product.objects.filter(color = i)

        colorWithProducts = {
        'id':id,
        'color':color,
        'hasProducts':hasProducts,
        'colorProducts':colorProducts
        }
        colors.append(colorWithProducts)

    #Add Color
    if request.method == 'POST' and 'add_color_name' in request.POST:
        add_color_name = request.POST.get('add_color_name')
        color_product_list = request.POST.getlist('color_product_list')
        total_color_products = len(color_product_list)
        new_color_object = Color.objects.create(color = add_color_name)
        if total_color_products > 0:
            for i in color_product_list:
                colorProduct = Product.objects.get(id = i)
                colorProduct.color.add(new_color_object)
        
        messages.success(request,'Color created successfully!')
        return redirect('noksha:control_panel')

    #Add Products To Color
    if request.method == 'POST' and 'color_add_product_list' in request.POST:
        color_add_product_list = request.POST.getlist('color_add_product_list')
        color_object = Color.objects.get(id = request.POST.get('color_id'))
        for i in color_add_product_list:
            color_add_product = Product.objects.get(id = i)
            color_add_product.color.add(color_object)

        messages.success(request,'Product added to color successfully!')
        return redirect('noksha:control_panel')
    
    #Remove Products From Color
    if request.method == 'POST' and 'color_remove_product_list' in request.POST:
        color_remove_product_list = request.POST.getlist('color_remove_product_list')
        color_remove_object = Color.objects.get(id = request.POST.get('color_id'))
        for i in color_remove_product_list:
            color_add_product = Product.objects.get(id = i)
            color_add_product.color.remove(color_remove_object)

        messages.success(request,'Product removed from color successfully!')
        return redirect('noksha:control_panel')

    #Delete Color 
    if request.method == 'POST' and 'remove_color' in request.POST:
        delete_color_object = Color.objects.get(id = request.POST.get('remove_color'))
        delete_color_object.delete()

        messages.success(request,'Color deleted successfully!')
        return redirect('noksha:control_panel')

    context = {
        'total_customers':total_customers,
        'customers':customers,
        'delivery_charge_objects':delivery_charge_objects,
        'products':discount_products,
        'discounts':discounts,
        'categorys':categorys,
        'category_products':category_products,
        'sizes':sizes,
        'colors':colors,
        'cupon_objects':cupon_objects
    }
    return render(request,'shop/pages/controlPanel.html',context)


def customerDetails(request,pk):
    customer =  Customer.objects.get(id = pk)
    shipping = ShippingAddress.objects.get(customer = customer)
    orders = []
    tmp_orders =  Order.objects.filter(customer = customer, complete = True).order_by('-date_created')
    total_orders = tmp_orders.count()
    for i in tmp_orders:
        orders.append(orderFetch(i.id))
    context = {
            'name' : customer.user.first_name,
            'email' : customer.user.email,
            'image' : customer.profile_pic.url,
            'address' : shipping.address,
            'area': shipping.state,
            'city': shipping.city,
            'total_orders': total_orders,
            'orders':orders,
        }
    return JsonResponse({'details':context})

@shopowner_only
@allowed_users(allowed_roles=['admin'])
@login_required(login_url='noksha:login')
def shopBlogs(request):
    blogs = Blog.objects.all().order_by('-date_added')

    #Create Blog
    if request.method == 'POST' and 'name' in request.POST:
        name = request.POST.get('name')
        place = request.POST.get('place')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        description = request.POST.get('description')

        new_blog = Blog.objects.create(name = name, place = place)
        new_blog.description = description
        if image:
            new_blog.img = image
        if video:
            new_blog.video = video
        new_blog.save()
        messages.success(request,'Blog created successfully!')
        return redirect('noksha:shop_blogs')
    
    #Update Blog
    if request.method == 'POST' and 'blogName' in request.POST:
        blogID = request.POST.get('blogID')
        blogName = request.POST.get('blogName')
        blogPlace = request.POST.get('blogPlace')
        blogImage = request.FILES.get('blogImage')
        blogVideo = request.FILES.get('blogVideo')
        blogDescription = request.POST.get('blogDescription')

        update_blog =  Blog.objects.get(id = blogID)
        update_blog.name = blogName
        update_blog.place = blogPlace
        update_blog.description = blogDescription
        if blogImage:
            update_blog.img = blogImage
        if blogVideo:
            update_blog.video = blogVideo
        update_blog.save()

        messages.success(request,'Blog updated successfully!')
        return redirect('noksha:shop_blogs')

    #Delete Blog
    if request.method == 'POST' and 'blog_delete' in request.POST:
        blog = Blog.objects.get(id = request.POST.get('blog_delete'))
        blog.delete()
        messages.success(request,'Blog deleted successfully!')
        return redirect('noksha:shop_blogs')

    context = {
        'blogs':blogs,
    }
    return render(request,'shop/pages/blogs.html',context)