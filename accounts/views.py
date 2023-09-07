from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login
from django.http import HttpResponseRedirect,HttpResponse
from accounts.models import Cart,CartItems 
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Address

from products.models import *
# Create your views here.
from .models import Profile


def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        elif not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')

        

        
        else:
            messages.warning(request, 'Invalid credentials')
            return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')
    



def add_to_cart(request,uid):
    variant=request.GET.get('variant')
    product=Product.objects.get(uid=uid)


    try:
        user=request.user
        cart , _=Cart.objects.get_or_create(user=user,is_paid=False)
        print("Hum exist krte h bhaiya************************************************")
        print(cart)
    except:
        device=request.COOKIES['device']
        cart , _ =Cart.objects.get_or_create(device=device,is_paid=False)
        print('hum guest h bhaiya ****************************************')
        print(cart)

    cart_item=CartItems.objects.create(cart=cart,product=product,)
    if variant:
        variant=request.GET.get('variant')
        size_variant=SizeVariant.objects.get(size_name=variant)
        cart_item.size_variant=size_variant
        cart_item.save()






  

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def buy_now(request,uid):
    variant=request.GET.get('variant')
    product=Product.objects.get(uid=uid)


    try:
        user=request.user
        cart , _=Cart.objects.get_or_create(user=user,is_paid=False)
        print("Hum exist krte h bhaiya************************************************")
        print(cart)
    except:
        device=request.COOKIES['device']
        cart , _ =Cart.objects.get_or_create(device=device,is_paid=False)
        print('hum guest h bhaiya ****************************************')
        print(cart)

    cart_item=CartItems.objects.create(cart=cart,product=product,)
    if variant:
        variant=request.GET.get('variant')
        size_variant=SizeVariant.objects.get(size_name=variant)
        cart_item.size_variant=size_variant
        cart_item.save()

    return redirect('cart')


def cart(request):
    try:
        user=request.user
        cart_obj=Cart.objects.get_or_create(is_paid=False,user=user)
        print('***********')
        print("purnana hun")
        print(cart_obj[0].coupon)
        


    except Exception as e:
        print(e)
        print("new Create kr rhe bhaiya!********************************************")
        device=request.COOKIES['device']
        cart_obj=Cart.objects.get_or_create(is_paid=False,device=device)
        print(cart_obj.coupon)

    if request.method=='POST':
        coupon = request.POST.get('coupon')
        coupon_obj=Coupon.objects.filter(coupon_code__icontains=coupon)
        if not coupon_obj.exists():
            messages.warning(request,'Invalid Coupon')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

        if cart_obj[0].coupon:
            messages.warning(request,'Coupon already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

        if coupon_obj.first().is_expired:
            messages.warning(request,'Coupon expired')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        if cart_obj[0].get_cart_total() < coupon_obj.first().minimum_amount:
            messages.warning(request,f'Amount should be greater than {coupon_obj.first().minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        

        cart_obj[0].coupon=coupon_obj[0]
        cart_obj[0].save()
        print(cart_obj[0].cart_items.all())
        print('MADARCHOD')
        messages.success(request,f'Coupon Applied worth {coupon_obj.first().discount_price}')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



    
    context={'cart':cart_obj[0]}
    
    return render(request,'accounts/cart.html',context)

def remove_cart(request,cart_item_uid):
    try:
        cart_item=CartItems.objects.get(uid=cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def remove_coupon(request,cart_id):
    cart=Cart.objects.get(uid=cart_id)
    cart.coupon=None
    cart.save()
    messages.success(request,'Coupon Removed.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def success(request):
    order_id = request.GET.get('order_id')
    cart = Cart.objects.get(razor_pay_order_id=order_id)
    
    # address = Address.objects.filter(user=request.user).first()
    # cart.shipping_address = address
    cart.is_paid = True
    cart.save()

    return HttpResponse('Payment Success')


@login_required(login_url='login')
def makepayment(request):
    user=request.user
    countries = ['India', 'United States', 'United Kingdom']
    states=['Uttar Pradesh','Madhya Pradesh','Maharashtra','New Delhi','Karnataka','London','Las Vegas','Los Angeles']
    cart_obj=Cart.objects.get(is_paid=False,user=user)
    addresses=Address.objects.filter(user=user)

    if request.method=='POST':
        address_id=request.POST.get('radiobtn')
        
        
        if address_id:
            selected_address = Address.objects.get(uid=address_id)
            print(selected_address)
            if cart_obj.get_cart_total()>0:
                # payment=checkout(request)
                # print(payment)
                # return render(request,'accounts/checkout.html',{'selected_address':selected_address,'cart':cart_obj,'payment':payment})
                return checkout(request,selected_address)
            # client=razorpay.Client(auth=(settings.KEY,settings.SECRET))
            # payment=client.order.create({'amount':cart_obj.get_cart_total()*100,'currency':'INR','payment_capture':1})
            # cart_obj.razor_pay_order_id=payment['id']
            # cart_obj.save()
            # print('******************')
            # print(payment)
            # print('******************')
            
        

                

        

        else:
        
        
            print("kaam kr rha bhai")
            new_address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zipcode = request.POST.get('zipcode')
            country = request.POST.get('country')
            address=Address.objects.create(user=user,address=new_address,city=city,state=state,zipcode=zipcode
                                            ,country=country)
            address.save()    
    context={'addresses':addresses,'countries':countries,'states':states,}
    return render(request,'accounts/payment.html',context)
    



def checkout(request,selected_address):
    user=request.user
    cart_obj=Cart.objects.get(is_paid=False,user=user)
    client=razorpay.Client(auth=(settings.KEY,settings.SECRET))
    payment=client.order.create({'amount':cart_obj.get_cart_total()*100,'currency':'INR','payment_capture':1})
    cart_obj.razor_pay_order_id=payment['id']
    
    cart_obj.shipping_address = selected_address
    # print(a)
    cart_obj.save()
    # print('******************')
    # print(payment)
    # print('******************')
    context={'payment':payment,'selected_address':selected_address,'cart':cart_obj}
    return render(request,'accounts/checkout.html',context)
@login_required(login_url='login')
def profile(request):
    address=Address.objects.filter(user=request.user).first()
    print(address)
    context={'address':address}
    return render(request,'accounts/profile.html',context)

def address(request):
    address=Address.objects.filter(user=request.user)
    
    context={'addresses':address}
    return render(request,'accounts/address.html',context)

@login_required(login_url='login')
def remove_address(request,address_uid):
    try:
        address=Address.objects.get(uid=address_uid)
        address.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def edit(request):
    if request.method=='POST':
        user=request.user
        name=request.POST.get('fullname')
        fullname=name.split()
        if len(fullname)>1:
            user.first_name=fullname[0]
            user.last_name=fullname[1]
        else:
            user.first_name=fullname[0]
        user.save()
        user_address=Address.objects.filter(user=user).first()
        print(user_address)
        user_address.address=request.POST.get('address')
        print(user_address.address)
        user_address.city=request.POST.get('city')
        user_address.state=request.POST.get('state')
        user_address.zipcode=request.POST.get('zipcode')
        
        user_address.save()
        print(user_address)
        messages.success(request,'Saved Successfully!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    return render(request,'accounts/edit.html')

@login_required(login_url='login')
def orders(request):
    paid_carts = Cart.objects.filter(user=request.user, is_paid=True)
    cart_items = []

    for cart in paid_carts:
        cart_items.extend(cart.cart_items.all())
        # cart_addresses.append(cart.shipping_address)
    for i in cart_items:
        print(i.cart.shipping_address)


    context = {'cart_items': cart_items,}
    return render(request, 'accounts/orders.html', context)