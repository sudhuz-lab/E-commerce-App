from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from ecommerceapp.models import Contact,Product
from django.contrib import messages
from math import ceil
from .models import Product
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required





# def index(request):
#     allProds = []
#     catprods = Product.objects.exclude(id__isnull=True).values('category', 'id')
#     cats = {item['category'] for item in catprods}
#     for cat in cats:
#         prod = Product.objects.filter(category=cat).exclude(id__isnull=True)
#         n = len(prod)
#         nSlides = ceil(n / 4)
#         allProds.append([prod, range(1, nSlides + 1), nSlides])
#     param = {'allProd': allProds}
#     return render(request, "index.html", param)
def index(request):
    products = Product.objects.exclude(id__isnull=True)
    cols = [[], [], [], []]
    for idx, prod in enumerate(products):
        cols[idx % 4].append(prod)
    param = {'columns': cols}
    return render(request, "index.html", param)

 


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")
        myquery = Contact(name = name,email=email,desc = desc,phonenumber = pnumber)
        myquery.save()
        messages.success(request, "We will get back to you soon.....")
        return render(request,"contact.html")

        
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {'product': product})




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Product

@csrf_exempt  # Use carefully, prefer AJAX CSRF token instead
def add_to_cart(request):
    if request.method == "POST":
        prod_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=prod_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})

        cart = request.session.get('cart', {})
        cart[prod_id] = cart.get(prod_id, 0) + 1
        request.session['cart'] = cart

        return JsonResponse({
            'success': True,
            'name': product.product_name,
            'price': str(product.price),
            'img': product.image.url,
        })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})




# def Shop_cart(request):
#     print(request.POST)  # Debug!
#     cart = request.session.get('cart', {})
#     products = Product.objects.filter(id__in=cart.keys())
#     cart_items = []
#     cart_total = 0

#     # Handle POST for cart update/removal
#     if request.method == "POST":
#         # Remove item
#         if 'remove' in request.POST:
#             prod_id = request.POST.get('remove')
#             if prod_id in cart:
#                 del cart[prod_id]
#                 request.session['cart'] = cart
#         # Update quantities
#         elif 'update_cart' in request.POST:
#             for product in products:
#                 qty_field = f"qty_{product.id}"
#                 if qty_field in request.POST:
#                     qty = int(request.POST[qty_field])
#                     if qty > 0:
#                         cart[str(product.id)] = qty
#                     else:
#                         cart.pop(str(product.id), None)
#             request.session['cart'] = cart

#     # Re-fetch cart after update/removal
#     products = Product.objects.filter(id__in=cart.keys())
#     cart_items = []
#     cart_total = 0

#     for product in products:
#         quantity = cart.get(str(product.id), 0)
#         subtotal = product.price * quantity
#         cart_total += subtotal
#         cart_items.append({
#             'product': product,
#             'quantity': quantity,
#             'subtotal': subtotal,
#         })

#     return render(request, 'shop_cart.html', {
#         'cart_items': cart_items,
#         'cart_total': cart_total
#     })
def Shop_cart(request):
    cart = request.session.get('cart', {})
    print(f"Initial cart data: {cart}")

    products = Product.objects.filter(id__in=[int(pk) for pk in cart.keys()])
    cart_items = []
    cart_total = 0

    if request.method == "POST":
        print(f"POST data received: {request.POST}")

        if 'remove' in request.POST:
            prod_id = request.POST.get('remove')
            print(f"Removing product: {prod_id}")
            if prod_id in cart:
                del cart[prod_id]
                request.session['cart'] = cart
                print(f"Cart after removal: {cart}")

        elif 'update_cart' in request.POST:
            for product in products:
                qty_field = f"qty_{product.id}"
                if qty_field in request.POST:
                    try:
                        qty = int(request.POST[qty_field])
                    except ValueError:
                        qty = 0
                    print(f"Updating product {product.id} quantity to {qty}")
                    if qty > 0:
                        cart[str(product.id)] = qty
                    else:
                        cart.pop(str(product.id), None)
            request.session['cart'] = cart
            print(f"Cart after update: {cart}")

    products = Product.objects.filter(id__in=[int(pk) for pk in cart.keys()])
    cart_items = []
    cart_total = 0

    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity
        cart_total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })
        print(f"Product: {product.id}, Qty: {quantity}, Subtotal: {subtotal}")

    return render(request, 'shop_cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })


def Shop_order_complete(request):
    return render(request,"shop_order_complete.html")


from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
import razorpay
from .models import Product, Order, OrderItem

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
import razorpay
from .models import Product, Order, OrderItem

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=[int(k) for k in cart.keys()])

    if not products.exists():
        # Handle empty cart gracefully
        return render(request, 'checkout.html', {'cart_items': [], 'cart_total': 0})

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        province = request.POST.get('province')

        # Calculate total amount from cart
        total_amount = 0
        for product in products:
            quantity = cart.get(str(product.id), 0)
            total_amount += product.price * quantity

        print("Calculated Total Amount (₹):", total_amount)  # Debug

        # Create order in database (initially unpaid)
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postcode=postcode,
            province=province,
            paid=False,
        )

        # Save each cart item as an OrderItem
        for product in products:
            quantity = cart.get(str(product.id), 0)
            if quantity > 0:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

        # Razorpay expects amount in paise (multiply by 100)
        amount_in_paise = int(total_amount * 100)

        # Create Razorpay order
        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": "0"
        })

        # Save Razorpay order ID in our Order model
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        # ✅ Clear the cart AFTER creating the order
        request.session['cart'] = {}

        # Context for the payment page
        context = {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
            'amount': amount_in_paise,          # for Razorpay JS (paise)
            'display_amount': total_amount,     # for showing ₹ to user
            'currency': 'INR',
            'callback_url': '/paymenthandler/', # payment verification URL
        }
        return render(request, 'payment.html', context)

    # If GET request — show cart summary before payment
    cart_items = []
    cart_total = 0
    for product in products:
        quantity = cart.get(str(product.id), 0)
        subtotal = product.price * quantity
        cart_total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

    
    
    
    
    
    
    



from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import razorpay

from decimal import Decimal

def create_payment(request):
    # Example: get amount in rupees from cart/order
    order = ... # Fetch or calculate current order based on session or user

    # Calculate the order total (in rupees)
    order_total = sum(
        item.price * item.quantity for item in order.items.all()
    )

    amount_in_paise = int(order_total * Decimal('100'))  # for Razorpay

    currency = 'INR'
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create(dict(amount=amount_in_paise, currency=currency, payment_capture='0'))

    context = {
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'amount': amount_in_paise,        # for Razorpay JS
        'display_amount': order_total,    # for showing to user
        'currency': currency,
        'callback_url': '/paymenthandler/',
    }
    return render(request, 'payment.html', context)



from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import razorpay
from .models import Order

@csrf_exempt
def paymenthandler(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
        }
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature(params_dict)
            
            # Fetch order to get amount
            order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
            # Calculate subtotal in Decimal
            order_subtotal = sum(
                item.price * item.quantity for item in order.items.all()
            )
            # Razorpay expects amount in paise as integer
            amount_in_paise = int(order_subtotal * 100)

            # Capture payment with correct amount
            client.payment.capture(payment_id, amount_in_paise)

            # Update order payment fields
            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.paid = True
            order.save()

            # VAT in Decimal
            order_vat = (order_subtotal * Decimal('0.18')).quantize(Decimal('0.01'))
            order_total = (order_subtotal + order_vat).quantize(Decimal('0.01'))

            return render(request, 'paymentsuccess.html', {
                'order': order,
                'order_subtotal': order_subtotal,
                'order_vat': order_vat,
                'order_total': order_total
            })
        except razorpay.errors.SignatureVerificationError:
            return render(request, 'paymentfail.html')

    return HttpResponseBadRequest('Invalid request method')


from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def account_dashboard(request):
    user = request.user
    # Grab user's basic info (name, email, etc.)
    user_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]  # recent 5 orders
    return render(request, "account_dashboard.html", {
        "user": user,
        "orders": user_orders
    })
    
@login_required
def account_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'account_orders.html', {'orders': orders})
