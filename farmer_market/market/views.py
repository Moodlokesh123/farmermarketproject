from django.shortcuts import render, redirect, get_object_or_404
from .models import Crop, Farmer, Buyer, Order
from .forms import CropForm, FarmerForm, BuyerForm


# -----------------------------
# Home Page
# -----------------------------
def home(request):
    return render(request, 'home.html')


# -----------------------------
# Farmer Section
# -----------------------------
def register_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = FarmerForm()
    return render(request, 'register_farmer.html', {'form': form})


def farmer_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            farmer = Farmer.objects.get(email=email, password=password)
            request.session['farmer_id'] = farmer.id
            return redirect('farmer_dashboard')
        except Farmer.DoesNotExist:
            return render(request, 'farmer_login.html',
                          {'error': 'Invalid email or password'})
    return render(request, 'farmer_login.html')


def farmer_dashboard(request):
    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    farmer = Farmer.objects.get(id=request.session['farmer_id'])
    crops = Crop.objects.filter(farmer=farmer)
    orders = Order.objects.filter(crop__farmer=farmer)

    return render(request, 'farmer_dashboard.html', {
        'crops': crops,
        'orders': orders
    })


def add_crop(request):
    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    form = CropForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        crop = form.save(commit=False)
        crop.farmer_id = request.session['farmer_id']
        crop.save()
        return redirect('farmer_dashboard')

    return render(request, 'add_crop.html', {'form': form})


def edit_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)

    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES, instance=crop)
        if form.is_valid():
            form.save()
            return redirect('farmer_dashboard')
    else:
        form = CropForm(instance=crop)

    return render(request, 'edit_crop.html', {'form': form})


def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)
    crop.delete()
    return redirect('farmer_dashboard')


def farmer_orders(request):
    if 'farmer_id' not in request.session:
        return redirect('farmer_login')

    orders = Order.objects.filter(crop__farmer_id=request.session['farmer_id'])
    return render(request, 'farmer_orders.html', {'orders': orders})


# -----------------------------
# Marketplace
# -----------------------------
def marketplace(request):
    crops = Crop.objects.all()

    # Search
    query = request.GET.get('q')
    if query:
        crops = crops.filter(crop_name__icontains=query)

    # Price filter
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    if min_price and max_price:
        crops = crops.filter(price__range=(min_price, max_price))

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        crops = crops.filter(category_id=category_id)

    return render(request, 'marketplace.html', {'crops': crops})


# -----------------------------
# Cart System
# -----------------------------
def add_to_cart(request, crop_id):
    cart = request.session.get('cart', {})

    if str(crop_id) in cart:
        cart[str(crop_id)] += 1
    else:
        cart[str(crop_id)] = 1

    request.session['cart'] = cart
    return redirect('view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for crop_id, quantity in cart.items():
        crop = Crop.objects.get(id=crop_id)
        subtotal = crop.price * quantity
        total += subtotal

        cart_items.append({
            'crop': crop,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def increase_quantity(request, crop_id):
    cart = request.session.get('cart', {})
    if str(crop_id) in cart:
        cart[str(crop_id)] += 1
    request.session['cart'] = cart
    return redirect('view_cart')


def decrease_quantity(request, crop_id):
    cart = request.session.get('cart', {})
    if str(crop_id) in cart:
        cart[str(crop_id)] -= 1
        if cart[str(crop_id)] <= 0:
            del cart[str(crop_id)]
    request.session['cart'] = cart
    return redirect('view_cart')


def remove_from_cart(request, crop_id):
    cart = request.session.get('cart', {})
    if str(crop_id) in cart:
        del cart[str(crop_id)]
    request.session['cart'] = cart
    return redirect('view_cart')


# -----------------------------
# Buy Now
# -----------------------------
def buy_now(request, crop_id):
    request.session['buy_now_crop'] = crop_id
    return redirect('payment')


# -----------------------------
# Place Order From Cart
# -----------------------------
def place_order(request):
    request.session['cart_order'] = True
    return redirect('payment')


# -----------------------------
# Payment Page
# -----------------------------
def payment(request):
    if 'buyer_id' not in request.session:
        return redirect('buyer_login')

    if request.method == "POST":
        buyer = Buyer.objects.get(id=request.session['buyer_id'])

        # Buy Now Order
        if 'buy_now_crop' in request.session:
            crop = Crop.objects.get(id=request.session['buy_now_crop'])

            Order.objects.create(
                buyer=buyer,
                crop=crop,
                quantity=1,
                status="Pending"
            )

            del request.session['buy_now_crop']

        # Cart Orders
        elif 'cart_order' in request.session:
            cart = request.session.get('cart', {})

            for crop_id, quantity in cart.items():
                crop = Crop.objects.get(id=crop_id)

                Order.objects.create(
                    buyer=buyer,
                    crop=crop,
                    quantity=quantity,
                    status="Pending"
                )

            request.session['cart'] = {}
            del request.session['cart_order']

        return redirect('buyer_orders')

    return render(request, 'payment.html')


# -----------------------------
# Buyer Section
# -----------------------------
def register_buyer(request):
    if request.method == "POST":
        form = BuyerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('buyer_login')
    else:
        form = BuyerForm()

    return render(request, 'register_buyer.html', {'form': form})


def buyer_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        buyer = Buyer.objects.filter(email=email, password=password).first()

        if buyer:
            request.session['buyer_id'] = buyer.id
            return redirect('buyer_dashboard')
        else:
            return render(request, 'buyer_login.html',
                          {'error': 'Invalid credentials'})

    return render(request, 'buyer_login.html')


def buyer_dashboard(request):
    if 'buyer_id' not in request.session:
        return redirect('buyer_login')

    crops = Crop.objects.all()
    orders = Order.objects.filter(buyer_id=request.session['buyer_id'])

    return render(request, 'buyer_dashboard.html', {
        'crops': crops,
        'orders': orders
    })


def buyer_orders(request):
    if 'buyer_id' not in request.session:
        return redirect('buyer_login')

    buyer = Buyer.objects.get(id=request.session['buyer_id'])
    orders = Order.objects.filter(buyer=buyer)

    return render(request, 'buyer_orders.html', {'orders': orders})


# -----------------------------
# Order Status Update (Farmer)
# -----------------------------
def approve_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Approved"
    order.save()
    return redirect('farmer_orders')


def reject_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Rejected"
    order.save()
    return redirect('farmer_orders')


def deliver_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Delivered"
    order.save()
    return redirect('farmer_orders')
def payment_success(request):
    return render(request, 'payment_success.html')