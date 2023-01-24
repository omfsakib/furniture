from django.urls import path
from . import views
from .views import *
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

app_name = 'noksha'

urlpatterns = [
    path('login/',views.loginUser,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('signup/',views.signUpUser,name="sign_up"),
    path('account/account_id=<str:pk>/',views.accountProfile,name="account_profile"),
    path('',views.home,name="home"),
    path('blogs/',views.blogs,name="blogs"),
    path('product_id=<str:pk>/',views.productView,name="product_view"),
    path('category/category_id=<str:pk>/',views.categoryView,name="category_view"),
    path('category/subcategory_id=<str:pk>/',views.subcategoryView,name="sub_category_view"),
    path('order/order_id=<str:pk>/',views.view_order,name="order_view"),
    path('blog/blog_id=<str:pk>/',views.blog,name="blog_view"),
    path('product/search=<str:searchtext>/',views.searchProduct,name="search_product"),
    path('cart/',views.cart,name="cart"),
    path('checkout/',views.checkout,name="checkout"),
    path('update_item/',views.updateItem, name="update_item"),
    path('shop/dashboard/',shopDashboard.as_view(), name="shop_dashboard"),
    path('shop/view/order/<str:pk>/',views.updateOrder, name = 'update-order'),
    path('shop/products/',views.products, name = 'products'),
    path('shop/blogs/',views.shopBlogs, name = 'shop_blogs'),
    path('shop/product_id=<str:pk>/',views.shopProductView,name="shop_product_view"),
    path('shop/store/setting/',views.storeSettings,name="store_setting"),
    path('shop/store/banner/<str:pk>/',views.bannerSetting,name="banner_setting"),
    path('shop/store/collection/<str:pk>/',views.collectionSetting,name="collection_setting"),
    path('shop/store/shopnow/<str:pk>/',views.shopnowSetting,name="shopnow_setting"),
    path('shop/store/create/order/',views.createOrder,name="create_order"),
    path('shop/store/customer/<str:phone>/',views.fetchCustomer,name="fetch_customer"),
    path('shop/store/control/panel/',views.controlPanel,name="control_panel"),
    path('shop/store/customer/details/<str:pk>/',views.customerDetails,name="customer_details"),
]