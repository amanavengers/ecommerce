from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


# Create your views here.

def home(request):
    products = Product.objects.all()
    n = len(products)
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 + ceil(n / 4 - n // 4)
        allprods.append([prod, range(1, nslides), nslides])

    params = {'allprods': allprods}
    return render(request, 'shop/home.html', params)


def searchMatch(query, item):
    query = query.lower()
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    return False


def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nslides = n // 4 + ceil(n / 4 - n // 4)
        if len(prod) != 0:
            allprods.append([prod, range(1, nslides), nslides])

    params = {'allprods': allprods, 'msg': ""}
    if len(allprods) == 0 or len(query) < 3:
        params['msg'] = "Please make sure to enter a relevent search item"
    return render(request, 'shop/Search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def tracker(request):
    if request.method == "POST":
        orderid = request.POST.get('orderid', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(ord_id=orderid, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderid)
                updates = []
                for item in update:
                    updates.append(
                        {'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].item_json},
                                          default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')


def productview(request, id):
    product = Product.objects.filter(id=id)
    return render(request, 'shop/productview.html', {'product': product[0]})


def checkout(request):
    thank = False
    if request.method == "POST":
        itemsJson = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        zipcode = request.POST.get('zipcode', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        order = Order(item_json=itemsJson, name=name, email=email, phone=phone,
                      address1=address1, address2=address2, city=city, state=state, zip_code=zipcode)
        order.save()
        update = OrderUpdate(order_id=order.ord_id,
                             update_desc="The order has been placed")
        update.save()
        ord_id = order.ord_id
        thank = True
        return render(request, 'shop/checkout.html', {"thank": thank, "id": ord_id})
    return render(request, 'shop/checkout.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contactus = Contact(name=name, email=email, phone=phone, desc=desc)
        contactus.save()
    return render(request, 'shop/contact.html')


class SellView(CreateView):
    model = Product
    template_name = 'shop/sell.html'
    fields = ['product_name', 'category', 'subcategory', 'price', 'desc', 'pub_date', 'img']
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def form_valid(self, form):
        if 'img' in self.request.FILES:
            form.instance.thumbnail = self.request.FILES['img']
        return super().form_valid(form)
