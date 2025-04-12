from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . inherit import cartData

from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index(request):
    products = Product.objects.all()
    cartItems = 0  # Default value

    if request.user.is_authenticated:
        try:
            # Ensure customer exists for the user
            if not hasattr(request.user, 'customer'):
                Customer.objects.create(user=request.user, name=request.user.username, email=request.user.email)
            
            # Get the number of cart items from the Order model
            order = Order.objects.get(customer=request.user.customer, complete=False)
            cartItems = order.get_cart_items
        except Order.DoesNotExist:
            cartItems = 0

    return render(request, "index.html", {'products': products, 'cartItems': cartItems})


def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart:', cart)

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order["get_cart_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'image':product.image,
                },
                'quantity':cart[i]["quantity"],
                'get_total':total
            }
            items.append(item)
        except:
            pass
    return render(request, "cart.html", {'items':items, 'order':order, 'cartItems':cartItems})

def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    total = order.get_cart_total
    if request.method == "POST":
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        zipcode = request.POST['zipcode']
        phone_number = request.POST['phone_number']
        payment = request.POST['payment']
        shipping_adress = CheckoutDetail.objects.create(address=address, city=city, phone_number=phone_number, state=state, zipcode=zipcode, customer=request.user.customer, total_amount=total, order=order, payment=payment)
        shipping_adress.save()
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        id = order.id  
        alert = True
        return render(request, "checkout.html", {'alert':alert, 'id':id})
    return render(request, "checkout.html", {'items':items, 'order':order, 'cartItems':cartItems})

def updateItem(request):
    data = json.loads(request.body)
    productID = data['productID']
    action = data['action']

    print('Action:', action)
    print('productID:', productID)

    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    update_order, created = UpdateOrder.objects.get_or_create(order_id=order, desc="Your Order is Successfully Placed.")

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    update_order.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)

def product_view(request, myid):
    product = Product.objects.filter(id=myid).first()
    feature = Feature.objects.filter(product=product)
    reviews = Review.objects.filter(product=product)
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    if request.method=="POST":
        content = request.POST['content']
        review = Review(customer=Customer, content=content, product=product)
        review.save()
        return redirect(f"/product_view/{product.id}")
    return render(request, "product_view.html", {'product':product, 'cartItems':cartItems, 'feature':feature, 'reviews':reviews})

def search(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        search = request.POST['search']
        products = Product.objects.filter(name__contains=search)
        return render(request, "search.html", {'search':search, 'products':products, 'cartItems':cartItems})
    else:
        return render(request, "search.html")


def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "change_password.html", {'alert':alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong':currpasswrong})
        except:
            pass
    return render(request, "change_password.html", {'cartItems':cartItems})

def contact(request):
    if request.method=="POST":       
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'contact.html', {'alert':alert})
    return render(request, "contact.html")

def loggedin_contact(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method=="POST":       
        name = request.user
        email = request.user.email
        phone = request.user.customer.phone_number
        desc = request.POST['desc']
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        alert = True
        return render(request, 'loggedin_contact.html', {'alert':alert})
    return render(request, "loggedin_contact.html", {'cartItems':cartItems})

def tracker(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']
    if request.method == "POST":
        order_id = request.POST['order_id']
        order = Order.objects.filter(id=order_id).first()
        order_items = OrderItem.objects.filter(order=order)
        update_order = UpdateOrder.objects.filter(order_id=order_id)
        print(update_order)
        return render(request, "tracker.html", {'order_items':order_items, 'update_order':update_order})
    return render(request, "tracker.html", {'cartItems':cartItems})

def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST.get('username', '').strip()
            full_name = request.POST.get('full_name', '').strip()
            password1 = request.POST.get('password1', '').strip()
            password2 = request.POST.get('password2', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            email = request.POST.get('email', '').strip()

            # Validate form inputs
            if not username or not full_name or not email or not password1 or not password2:
                messages.error(request, "All fields are required.")
                return render(request, "register.html")

            if password1 != password2:
                messages.error(request, "Passwords do not match!")
                return render(request, "register.html")

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
                return render(request, "register.html")

            # Create User
            user = User.objects.create_user(username=username, password=password1, email=email)

            # Ensure Customer does not already exist
            customer, created = Customer.objects.get_or_create(user=user, defaults={
                "name": full_name,
                "phone_number": phone_number,
                "email": email
            })

            messages.success(request, "Registration successful! Please log in.")
            return redirect("/login/")

    return render(request, "register.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "Invalid username or password")
                return render(request, "login.html")

    return render(request, "login.html")

def Logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("/")