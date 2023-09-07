
from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/',views.login_page,name='login'),
    path('register/',views.register_page,name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add-to-cart/<uid>/',views.add_to_cart,name='add_to_cart'),
    path('buy-now/<uid>/',views.buy_now,name='buy_now'),

    path('activate/<email_token>/' , views.activate_email , name="activate_email"),
    path('remove_cart/<cart_item_uid>/',views.remove_cart,name='remove_cart'),
    path('cart/',views.cart,name='cart'),
    path('remove_coupon/<cart_id>/',views.remove_coupon,name='remove_coupon'),
    path('success/',views.success,name='success'),
    path('payment/',views.makepayment,name='payment'),
    path('checkout/',views.checkout,name='checkout'),
    path('profile/',views.profile,name='profile'),
    path('address/',views.address,name='address'),
    path('edit_profile/',views.edit,name='edit'),
    path('remove_address/<address_uid>/',views.remove_address,name='remove_address'),
    path('orders/',views.orders,name='orders')
    
] 
