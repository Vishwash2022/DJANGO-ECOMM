from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.models import User 
from django.db.models import Q
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate

 
#def home(request):
 #return render(request, 'app/home.html')
 
class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears= Product.objects.filter(category='BW')
        mobiles= Product.objects.filter(category='M')
        laptops= Product.objects.filter(category='L')
        return render(request, 'app/home.html',
        {'topwears':topwears, 'bottomwears':bottomwears, 'mobiles': mobiles,"laptops":laptops})
        
class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
            return render(request, 'app/productdetail.html',{'product':product, 'item_already_in_cart':item_already_in_cart})
        else:
            return render(request, 'app/productdetail.html',{'product':product, 'item_already_in_cart':item_already_in_cart})

def add_to_cart(request):
    user = request.user
    product_id =request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    #cart=Cart.objects.create(User=User, product=product)
    #cart.save()
    return redirect('/cart')


       
# def add_to_cart(request):
# 	user = request.user  #to get the current user 
# 	item_already_in_cart1 = False
# 	product = request.GET.get('prod_id')
# 	item_already_in_cart1 = Cart.objects.filter(Q(product=product) & Q(user=request.user)).exists()
# 	if item_already_in_cart1 == False:
# 		product_title = Product.objects.get(id=product)
# 		Cart(user=user, product=product_title).save()
# 		messages.success(request, 'Product Added to Cart Successfully !!' )
# 		return redirect('/cart')
# 	else:
# 		return redirect('/cart')


def show_cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart= Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount=70.0
        total_amount=0.0
        cart_product=[p for p in Cart.objects.all() if p.user == user]
        print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount=(p.quantity*p.product.discounted_price)
                amount+= tempamount
                total_amount=amount+shipping_amount
            return render(request, 'app/addtocart.html',{'carts':cart, 'total_amount':total_amount, 'amount':amount})
        else:
            return render(request, 'app/emptycart.html')
    else:
        return render(request, 'app/emptycart.html')
        

def plus_cart(request):
    if request.method == 'GET':
        prod_id= request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        amount =0.0
        shipping_amount=70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+= tempamount
            

        data ={
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
            }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id= request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount =0.0
        shipping_amount=70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+= tempamount
            

        data ={
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
            }
        return JsonResponse(data)
    
def remove_cart(request):
    if request.method == 'GET':
        prod_id= request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount =0.0
        shipping_amount=70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+= tempamount

        data ={
             'amount': amount,
            'totalamount': amount + shipping_amount
            }
        return JsonResponse(data)
    
    
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=70.0
    totalamount= 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount+= tempamount
        totalamount= amount+ shipping_amount
    return render(request, 'app/checkout.html',{'add': add, 'totalamount':totalamount, 'cart_items':cart_items})

def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart= Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Congratulation!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})
    

class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render (request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr= request.user 
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Congratulation!! Profile Updated Succesfully')
        return render (request, 'app/profile.html', {'form':form, 'active':'btn-primary'})


def product_detail(request):
 return render(request, 'app/productdetail.html')

# def add_to_cart(request):
#  return render(request, 'app/addtocart.html')

def buy_now(request):
 return render(request, 'app/buynow.html')

# def profile(request):
#  return render(request, 'app/profile.html')

def address(request):
 return render(request, 'app/address.html')

def orders(request):
 return render(request, 'app/orders.html')

def change_password(request):
 return render(request, 'app/changepassword.html')

def mobile(request):
 return render(request, 'app/mobile.html')

#def login(request):
# return render(request, 'app/login.html')

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

#def checkout(request):
# return render(request, 'app/checkout.html')

def user_login(request):
 if not request.user.is_authenticated:
  if request.method == "POST":
   form = LoginForm(request=request, data=request.POST)
   if form.is_valid():
    uname = form.cleaned_data['username']
    upass = form.cleaned_data['password']
    user = authenticate(username=uname, password=upass)
    if user is not None:
     login(request, user)
     messages.success(request, 'Logged in Successfully !!')
     return HttpResponseRedirect('/base.html')
  else:
   form = LoginForm()
  return render(request, 'blog/login.html', {'form':form})
 else:
  return HttpResponseRedirect('/login/')

def mobile(request):
        mobiles = Product.objects.filter(category='M')
        return render(request, 'app/mobile.html',{'mobiles':mobiles})
    
def laptop(request):
    laptop =Product.objects.filter(category='L')
    return render(request,'app/laptop.html',{'laptop':laptop})

def topwear(request):
    topwear=Product.objects.filter(category='TW')
    return render(request,'app/topwear.html',{'topwears':topwear})

def bottomwear(request):
    bottomwear=Product.objects.filter(category='BW')
    return render(request,'app/bottomwear.html',{'bottomwears':bottomwear})

def search(request):
    if request.method=='POST':  
        p_name=request.POST['search']
        product=Product.objects.filter(brand=p_name)
        return render(request,'app/searchresult.html',{'Product':product})