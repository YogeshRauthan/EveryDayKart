from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json

# Create your views here.
# commit1

def index(request):

    allProds = []
    allCategory = Product.objects.values('category', 'id')
    cats = {item['category'] for item in allCategory}

    for x in cats:
        prodcat = Product.objects.filter(category=x)
        n = len(prodcat)
        nSlides = ceil((n/4))
        allProds.append([prodcat, range(1,nSlides), nSlides])

    params = {'allProducts':allProds}

    return render(request,'shop/index.html', params)


def about(request):
    return render(request,'shop/about.html')


def proddetails(request):
    all_prods = Product.objects.all()
    context = {'Prods' : all_prods,}

    return render(request, 'shop/seeproductdetails.html', context)


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name','')
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        print(name,email,phone,desc)
        contact1 = Contact(name=name, email=email, phone=phone, desc=desc)
        contact1.save()
        thank = True

    return render(request,'shop/contact.html',{'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId','')
        email = request.POST.get('email','')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc, 'time':item.timestamp})
                    response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                
                return HttpResponse(response)
            
            else:
                return HttpResponse('{"status": "noitem"}')
            
        except Exception as e:
            return HttpResponse('{"status": "error"}')

    return render(request,'shop/tracker.html')


def search(request):
    query = request.GET.get('search')
    allProds = []
    allCategory = Product.objects.values('category', 'id')
    cats = {item['category'] for item in allCategory}

    for x in cats:
        prodcattemp = Product.objects.filter(category=x)
        prodcat = [item for item in prodcattemp if searchMatch(query, item)]
        n = len(prodcat)
        nSlides = ceil((n/4))
        if len(prodcat) != 0:
            allProds.append([prodcat, range(1,nSlides), nSlides])

    params = {'allProducts':allProds, 'msg': ""}
    if len(allProds) == 0 or len(query) < 3:
        params = {'msg': "Please make sure to enter relevent search query"}

    return render(request,'shop/search.html', params)

def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def productview(request, myid):
    # Fetch the product using id
    product_id = Product.objects.filter(id=myid)

    return render(request,'shop/productview.html', {'productid':product_id[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        order = Order(items_json=items_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone)
        order.save()

        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()

        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})

    return render(request,'shop/checkout.html')