from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Customer, Order, Item, OrderItem, Category, Store_Order, Store_OrderItem
from .forms import CategoryForm, CustomerForm, ItemForm
from decimal import Decimal
import datetime
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


def login_view(request):
    if request.method == 'GET':
        full_url = request.get_full_path()
        index_url = full_url.find('=')
        if index_url > 0 :
            url = full_url[index_url + 1:]
        else:
            url = 0
        return render(request, "main/login.html", {
            "url": url,
        })

    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            url = request.POST["url"]
            if url and url != "0":
                return HttpResponseRedirect(url)
            return HttpResponseRedirect("/")
                
        else:
            return render(request, "main/login.html", {
                "err_message": "هناك خطأ في الأسم او الرقم السري"
            })

def logout_view(request):
    logout(request)
    return render(request, "main/login.html", {
            "success_message": "تم تسجيل خروجك بنجاح "
        })

@login_required(login_url="/login/")
def make_order(request):
    items_object = {}
    categories = Category.objects.all()
    for category in categories:
        items = Item.objects.filter(category=category).order_by('id')
        items_object[f"{category.name}"] = items

    
    if request.method == 'GET':
        customers = Customer.objects.all()
        return render(request, "main/make_order.html", {
            "items_object": items_object,
            "customers": customers,
        })
        
    else:
        customer_id = request.POST["customer"]
        customer = Customer.objects.get(id=customer_id)

        market_or_gomla = request.POST["market_or_gomla"]
        
        check_order = False
        if market_or_gomla == "market":
            order = Order.objects.create(customer=customer)
        else:
            order = Order.objects.create(customer=customer, is_gomla=True)
        
        for category in items_object.values():
            for item in category:
                try:
                    quantity = int(request.POST[f"quantity_{item.id}"])
                except ValueError:
                    quantity = 0
                if quantity > 0:
                    OrderItem.objects.create(order=order, item=item, quantity=quantity)
                    check_order = True

        if check_order == False:
            order.delete()
            return HttpResponseRedirect("/")

        return HttpResponseRedirect(f"/order_info/{order.id}")
        
@login_required(login_url="/login/")
def add_items(request, order_id): 
    order = get_order(order_id)
    if not order:
        return HttpResponseRedirect(f"/order_error/{order_id}")
    
    items_object = {}
    categories = Category.objects.all()
    un_wanted_items = OrderItem.objects.filter(order=order).values_list('item', flat=True)

    for category in categories:
        items = Item.objects.exclude(id__in=un_wanted_items)
        items_object[f"{category.name}"] = items.filter(category=category)

    if request.method == "GET":
        return render(request, "main/add_items.html", {
            "items_object": items_object,
            "order": order
        })
        
    else:
        for category in items_object.values():
            for item in category:
                try:
                    quantity = int(request.POST.get(f"quantity_{item.id}"))
                except ValueError:
                    quantity = 0

                if quantity > 0:
                    OrderItem.objects.create(order=order, item=item, quantity=quantity)

        return HttpResponseRedirect(f"/order_info/{order_id}")


@login_required(login_url="/login/")
def order_info(request, order_id):
    order = get_order(order_id)
    if not order:
        return HttpResponseRedirect(f"/order_error/{order_id}")
    order_items = OrderItem.objects.filter(order=order)
    return render(request, "main/order_info.html", {
        "order":order,
        "order_items":order_items,
    })     

        
        
@login_required(login_url="/login/")
def users(request):
    if request.method == 'GET':
        customers = Customer.objects.all().order_by("-is_shop", "id")
        orders = Order.objects.filter(is_used=True).order_by("-id")
        return render(request, "main/users_display.html", {
            "customers": customers,
            "orders": orders,
        })
    else:
        customer_id = request.POST["customer_id"]
        order_id = request.POST["order_id"]

        if customer_id and not order_id:
            if customer_id.isnumeric():
                return HttpResponseRedirect(f"{customer_id}")
            else:
                customer_name_for_id = Customer.objects.filter(name__contains=customer_id).first()
                if customer_name_for_id:
                    return HttpResponseRedirect(f"{customer_name_for_id.id}")
        elif order_id.isnumeric() and not customer_id:
            return HttpResponseRedirect(f"/order_info/{order_id}")

        return HttpResponseRedirect("/users/")

@login_required(login_url="/login/")
def all_orders(request):
    orders = Order.objects.filter(is_used=True).order_by("-created_at")
    dates = orders.values_list("created_at", flat=True); years = {}
    for date in dates:
        date = change_zone(date)
        if not date.year in years.keys():
            years[f"{date.year}"] = orders.filter(created_at__range=(datetime.date(date.year, 1, 1), datetime.date(date.year + 1, 1, 1)))

    return render(request, "main/all_orders.html", {
        "years": years,
    })

@login_required(login_url="/login/")
def all_coming_orders(request):
    orders = Store_Order.objects.all().order_by("-created_at")
    dates = orders.values_list("created_at", flat=True); years = {}
    for date in dates:
        date = change_zone(date)
        if not date.year in years.keys():
            years[f"{date.year}"] = orders.filter(created_at__range=(datetime.date(date.year, 1, 1), datetime.date(date.year + 1, 1, 1)))

    return render(request, "main/all_coming_orders.html", {
        "years": years,
    })
        

@login_required(login_url="/login/")
def user(request, user_id):
    if request.method == 'GET':
        customer = Customer.objects.filter(id=user_id).first()
        if customer:
            arranged_orders = {}
            orders = customer.orders.all().order_by('-created_at')
            for order in orders:
                order_time = change_zone(order.created_at)

                y = order_time.strftime("%y")
                m = order_time.strftime("%m")
                d = order_time.strftime("%d")
                if str(y) not in arranged_orders.keys():
                    arranged_orders[f"{y}"] = {}
                if str(m) not in arranged_orders[f"{y}"].keys():
                    arranged_orders[f"{y}"][f"{m}"] = {}
                if str(d) not in arranged_orders[f"{y}"][f"{m}"].keys():
                    arranged_orders[f"{y}"][f"{m}"][f"{d}"] = []
                arranged_orders[f"{y}"][f"{m}"][f"{d}"].append(order)

            total_orders_info = get_total_orders_info(customer, "all")
            rest_info = get_rest_info(customer)
            total_money = get_total_orders_info(customer, 0)

            if not total_orders_info:
                return render(request, "main/user_display.html", {
                    "customer": customer,
                    "orders": orders,
                    "arranged_orders": arranged_orders,
                    "total_orders_info": total_orders_info,
                })

            if total_orders_info and rest_info and total_money:
                percent = (total_money - rest_info["rest_money"]) / total_money * 100
            elif total_orders_info and not rest_info:
                percent = 100

            return render(request, "main/user_display.html", {
                "customer": customer,
                "orders": orders,
                "arranged_orders": arranged_orders,
                "total_orders_info": total_orders_info,
                "rest_info": rest_info,
                "percent": int(percent),
            })

        else:
            return render(request, "main/error.html", {
                "message": f"العميل رقم {user_id} غير موجود",
                "message2": "ابحث عن عميل اخر"
            })

    else:
        order_id = request.POST["order_id"]
        order = get_order(order_id)
        if not order:
            return HttpResponseRedirect(f"/order_error/{order_id}")
        return HttpResponseRedirect(f"/edit_order/{order.id}")




@login_required(login_url="/login/")
def edit_order (request, order_id):
    order = get_order(order_id)
    if not order:
        return HttpResponseRedirect(f"/order_error/{order_id}")
    
    if request.method == 'GET':
        is_gomla = order.is_gomla
        order_items = OrderItem.objects.filter(order=order)
        return render(request, "main/order_info.html", {
            "order":order,
            "order_items":order_items,
            "is_gomla":is_gomla,
            "message_edit": "تم حفظ التعديل",
        })     
    
    else:
        if int(request.POST["new_discount"]) != int(order.discount):
            update_discount(order, int(request.POST["new_discount"]))
            return HttpResponseRedirect(f"{order.id}")
    
        else:
            if order.total_order_price != Decimal(request.POST["total_order_price"]):
                order.update_total_prices(Decimal(request.POST["total_order_price"]))

            else:
                order_items = OrderItem.objects.filter(order=order)

                for order_item in order_items:
                    new_quantity = request.POST[f"quantity_{order_item}"]
                    try:
                        if int(new_quantity) < 1:
                            order_item.delete()
                        else:
                            order_item.quantity = Decimal(new_quantity)
                            order_item.save()
                    except ValueError:
                        order_item.delete()
                order.update_same_disc()
                update_items()

                if not OrderItem.objects.filter(order=order):
                    order.delete()
                    return HttpResponseRedirect("/users/")

            return HttpResponseRedirect(f"{order.id}")
        
@login_required(login_url="/login/")
def change_rest(request):
    try:
        order_id = int(request.GET.get("order_id"))
    except ValueError:
        return render(request, "main/change_rest.html", {
            "err": f"لا يمكن البحث عن طلب ب الاحرف او الرموز"
        })

    order = get_order(order_id)

    if not order:
        return HttpResponseRedirect(f"/order_error/{order_id}")


    if request.method == 'GET':
        return render(request, "main/change_rest.html", {
            "order": order,
        })

    else:
        rest_money = request.POST["rest_money"]
        if order.rest_money - Decimal(rest_money) > Decimal(-1):
            order.rest_money -= Decimal(rest_money)
            order.save()
            return HttpResponseRedirect(f"/order_info/{order_id}")
        else:
            return render(request, "main/change_rest.html", {
                "order": order,
                "err": f"لا يمكن اضافة قسط اعلي من قيمه الآجل"
            })

@login_required(login_url="/login/")
def coming_change_rest(request):
    try:
        order_id = int(request.GET.get("order_id"))
    except ValueError:
        return render(request, "main/coming_change_rest.html", {
            "err": f"لا يمكن البحث عن طلب ب الاحرف او الرموز"
        })
    order = get_coming_order(order_id)
    if not order:
        return render(request, "main/coming_change_rest.html", {
            "err": f"لا يوجد طلبية برقم {order_id}"
        })

    if request.method == 'GET':
        return render(request, "main/coming_change_rest.html", {
            "order": order,
        })

    else:
        rest_money = request.POST["rest_money"]
        if order.rest_money - Decimal(rest_money) > Decimal(-1):
            order.rest_money -= Decimal(rest_money)
            order.save()
            return HttpResponseRedirect(f"/coming_order/{order_id}")
        else:
            return render(request, "main/coming_change_rest.html", {
                "order": order,
                "err": f"لا يمكن اضافة قسط اعلي من قيمه الآجل"
            })

@login_required(login_url="/login/")
def put_rest(request):
    try:
        order_id = int(request.GET.get("order_id"))
    except ValueError:
        return render(request, "main/put_rest.html", {
            "err": f"لا يمكن البحث عن طلب ب الاحرف او الرموز"
        })
    order = get_order(order_id)
    if not order:
        return HttpResponseRedirect(f"/order_error/{order_id}")

    if request.method == 'GET':
        return render(request, "main/put_rest.html", {
            "order": order,
        })
            
    else:
        rest = request.POST["rest_money"]
        order.rest_money = Decimal(rest)
        order.is_fully_paid = False
        order.save()

        return HttpResponseRedirect(f"/order_info/{order_id}")


@login_required(login_url="/login/")
def coming_put_rest(request):
    try:
        order_id = int(request.GET.get("order_id"))
    except ValueError:
        return render(request, "main/coming_put_rest.html", {
            "err": f"لا يمكن البحث عن طلب ب الاحرف او الرموز"
        })
    order = get_coming_order(order_id)
    if not order:
        return render(request, "main/coming_put_rest.html", {
            "err": f"لا يوجد طلبية برقم {order_id}"
        })


    if request.method == 'GET':
        return render(request, "main/coming_put_rest.html", {
            "order": order,
        })
            
    else:
        rest = request.POST["rest_money"]
        order.rest_money = Decimal(rest)
        order.is_fully_paid = False
        order.save()
        return HttpResponseRedirect(f"/coming_order/{order_id}")
        

@login_required(login_url="/login/")
def change_rank(request, order_id):
    order = get_order(order_id)
    if not order:
        return HttpResponseRedirect(f"/order_error/{order_id}")
        
    if order.is_gomla:
        order.is_gomla = False
    else:
        order.is_gomla = True
    order.update_same_disc()
    for order_item in OrderItem.objects.filter(order=order):
        order_item.update_profit()

    return HttpResponseRedirect(f"/edit_order/{order_id}")
    
    



@login_required(login_url="/login/")
def delete_order(request, order_id):
    order = get_order(order_id)
    if not order:
        return HttpResponseRedirect(f"/order_error/{order_id}")
            
    if request.method == 'GET':
        return render(request, "main/delete_order.html", {
            "order": order,
        })
    else:
        order.delete() 
        update_items()
        return HttpResponseRedirect(f"/users/{order.customer.id}")


@login_required(login_url="/login/")
def delete_order_item(request, order_item_id):
    
    order_item = OrderItem.objects.get(pk=order_item_id)
    order_item.delete() ; update_items()

    order = Order.objects.get(pk=order_item.order.id)
    if not OrderItem.objects.filter(order=order):
        user_id = order.customer.id
        order.delete()
        return HttpResponseRedirect(f"/users/{user_id}")
    order.update_same_disc()
    return HttpResponseRedirect(f"/order_info/{order.id}")

    
@login_required(login_url="/login/")
def order_error(request, order_id):
    order = get_order(order_id)
    if not order:
        return render(request, "main/error.html", {
            "message": f"الطلب رقم {order_id} غير موجود",
            "message2": "البحث عن طلب اخر",
        })

    return HttpResponseRedirect(f"/order_info/{order.id}")   


@login_required(login_url="/login/")
def users_search(request, text):
    if request.method == 'GET':
        if text.isnumeric():
            text = int(text)
            if text % 10 == 0:
                customers = Customer.objects.filter(id__range=(text, text + 10))
            else:
                customers = Customer.objects.filter(id__contains=text )
        else:
            customers = Customer.objects.filter(name__contains=f"{text}")
        return JsonResponse([customer.serialize() for customer in customers], safe=False)

@login_required(login_url="/login/")
def create_item(request):
    item_form = ItemForm
    category_form = CategoryForm
    if request.method == 'GET':
        return render(request, "main/create_item.html", {
            "form": item_form,
            "category_form": category_form,
        })

    else:
        form = ItemForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            name = form.cleaned_data['name']
            real_price = form.cleaned_data['real_price']
            gomla_price = form.cleaned_data['gomla_price']
            market_price = form.cleaned_data['market_price']
            stock_quantity = form.cleaned_data['stock_quantity']
            Item.objects.create(category=category, name=name, real_price=real_price, gomla_price=gomla_price, stock_quantity=stock_quantity, market_price=market_price)

            return render(request, "main/create_item.html", {
                "form": item_form,
                "category_form": category_form,
                "success_message": f"بنجاح - {name} - تم أضافة المنتج "
            })

        else:
            return render(request, "main/create_item.html", {
                "form": item_form,
                "category_form": category_form,
                "err_message": "حدث خطأ في تسجيل المنتج من الممكن تشابه الاسم مع اخر موجود بالفعل",
            })

@login_required(login_url="/login/")
def create_category(request):
    item_form = ItemForm
    category_form = CategoryForm

    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_name = category_form.cleaned_data['name']
            Category.objects.create(name=category_name)

            return render(request, "main/create_item.html", {
                "form": item_form,
                "category_form": category_form,
                "success_message": f"بنجاح - {category_name} - تم أضافة النوع "
            })
            
        else:
            return render(request, "main/create_item.html", {
                "form": item_form,
                "category_form": category_form,
                "err_message": "حدث خطأ في تسجيل النوع من الممكن تشابه الاسم مع اخر موجود بالفعل",
            })

@login_required(login_url="/login/")
def create_customer(request):
    if request.method == 'GET':
        return render(request, "main/create_customer.html", {
            "form": CustomerForm,
        })

    else:
        form = CustomerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            number = form.cleaned_data['number']
            is_supplier = form.cleaned_data['is_supplier']
            Customer.objects.create(name=name, number=number, is_supplier=is_supplier)

            return render(request, "main/create_customer.html", {
                "form": CustomerForm,
                "success_message": f"بنجاح - {name} - تم أضافة العميل "                
            })
        else:
            return render(request, "main/create_customer.html", {
                "form": form,
                "err_message": "حدث خطأ في تسجيل العميل من الممكن تشابه الرقم مع اخر موجود بالفعل",
            })


@login_required(login_url="/login/")
def items_view(request):
    items = Item.objects.all().order_by("-used_quantity")
    return render(request, "main/items_view.html", {
        "items": items,
    })

@login_required(login_url="/login/")
def update_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'GET':
        return render(request, "main/update_item.html", {
            "item": item,
        })
    else:
        try:
            name = request.POST["name"]
    
            real_price = request.POST["real_price"]
            gomla_price = request.POST["gomla_price"]
            market_price = request.POST["market_price"]
            item.name = name
            item.real_price = Decimal(real_price)
            item.gomla_price = Decimal(gomla_price)
            item.market_price = Decimal(market_price)
            item.save()
            return render(request, "main/update_item.html", {
                "item": item,
                "success_message": "تم حفظ تعديلك بنجاح ",
            })
        except:
            return render(request, "main/update_item.html", {
                "item": item,
                "err_message": "حدث خطأ في تحديث بيانات المنتج ",
            })

@login_required(login_url="/login/")
def coming_order(request):
    items_object = {}
    categories = Category.objects.all()
    suppliers = Customer.objects.filter(is_supplier=True)
    for category in categories:
        items = Item.objects.filter(category=category).order_by('id')
        items_object[f"{category.name}"] = items

    
    if request.method == 'GET':
        customers = Customer.objects.filter(is_shop=True)
        return render(request, "main/create_store_order.html", {
            "items_object": items_object,
            "customers": customers,
            "suppliers": suppliers,
        })
        
    else:
        customer_id = request.POST["customer"]
        supplier_id = request.POST["supplier"]
        customer = Customer.objects.get(id=customer_id)
        supplier = Customer.objects.get(id=supplier_id)

        
        check_order = False
        order = Store_Order.objects.create(customer=customer, supplier=supplier)
        
        for category in items_object.values():
            for item in category:
                try:
                    quantity = int(request.POST[f"quantity_{item.id}"])
                except ValueError:
                    quantity = 0
                if quantity > 0:
                    Store_OrderItem.objects.create(
                        order=order, item=item, quantity=quantity,single_real_price=item.real_price,
                        single_gomla_price=item.gomla_price, single_market_price=item.market_price
                        )
                    check_order = True

        if check_order == False:
            order.delete()
            return HttpResponseRedirect("/coming_order")

        last_order = Store_Order.objects.all().exclude(id=order.id).order_by("-id").first()
        if last_order:
            last_order.is_done = True
            last_order.save()
        return HttpResponseRedirect(f"/coming_order/{order.id}")

@login_required(login_url="/login/")
def add_coming_items(request, order_id):

    order = get_object_or_404(Store_Order, pk=order_id)
    categories = Category.objects.all()
    items_object = {}

    un_wanted_items = Store_OrderItem.objects.filter(order=order).values_list('item', flat=True)
    for category in categories:
        al_items = Item.objects.filter(category=category).order_by('id')
        items = []
        for item in al_items:
            if not item.id in un_wanted_items:
                items.append(item)

        items_object[f"{category.name}"] = items

    if request.method == 'GET':
        return render(request, "main/create_store_order.html", {
            "items_object": items_object,
            "customer": order.customer,
            "order": order,
        })
    
    else:
        for category in items_object.values():
            for item in category:
                try:
                    quantity = int(request.POST[f"quantity_{item.id}"])
                except ValueError:
                    quantity = 0
                if quantity > 0:
                    Store_OrderItem.objects.create(
                        order=order, item=item, quantity=quantity,single_real_price=item.real_price,
                        single_gomla_price=item.gomla_price, single_market_price=item.market_price
                        )
        return HttpResponseRedirect(f"/coming_order/{order.id}")

@login_required(login_url="/login/")
def coming_order_info(request, order_id):

    order = get_object_or_404(Store_Order, pk=order_id)
    order_items = Store_OrderItem.objects.filter(order=order)
    return render(request, "main/coming_order_info.html", {
        "order": order,
        "order_items": order_items,
    })


@login_required(login_url="/login/")
def delete_coming_item(request, item_id):
    item = Store_OrderItem.objects.get(id=item_id)
    order_id = item.order.id
    if item.item.stock_quantity - item.quantity < item.item.used_quantity:
        return render(request, "main/error.html", {
                "message": f"لايمكن حذف العنصر {item.id}",
                "message4": f"لان الكميه المستهلكة ستكون اقل مما يمكن",
            })

    item.delete()
    return HttpResponseRedirect(f"/coming_order/{order_id}")

@login_required(login_url="/login/")
def edit_coming_item(request, item_id):
    if request.method == 'POST':
        item = Store_OrderItem.objects.get(id=item_id)
        quantity = request.POST[f"quantity_{item.id}"]
        single_real_price = request.POST[f"real_{item.id}"]
        single_gomla_price = request.POST[f"gomla_{item.id}"]
        single_market_price = request.POST[f"market_{item.id}"]

        if quantity and single_real_price and single_gomla_price and single_market_price:
            if int(quantity) < 1:
                item.delete()
            else:
                item.update_item_prices(reverse=True)
                item.quantity = int(quantity)
                item.single_real_price = Decimal(single_real_price)
                item.single_gomla_price = Decimal(single_gomla_price)
                item.single_market_price = Decimal(single_market_price)
                item.save()
            return HttpResponseRedirect(f"/coming_order/{item.order.id}")

@login_required(login_url="/login/")
def delete_coming_order(request, order_id):
    if request.method == 'GET':
        order = Store_Order.objects.get(pk=order_id)
        items = Store_OrderItem.objects.filter(order=order)
        check = True ; undeletable_items = []

        for item in items:
            if item.item.stock_quantity - item.quantity < item.item.used_quantity:
                undeletable_items.append(item.item.name)
                check = False

        if check == False:
            return render(request, "main/error.html", {
                "message": f"{undeletable_items} لايمكن حذف العناصر ",
                "message4": f"لان الكميه المستهلكة ستكون اقل مما يمكن",
                "message5": f"يمكنك فقط حذف المتبقي من العناصر في طلبيتك",
            })
        else:
            order.delete()
            last_order = Store_Order.objects.all().order_by("-id").first()
            if last_order:
                last_order.is_done = False
                last_order.save()
            return HttpResponseRedirect("/coming_order")

@login_required(login_url="/login/")
def done_coming_order(request, order_id):
    if request.method == 'GET':
        orders = Store_Order.objects.all()

        for order in orders:
            order.is_done = True
            order.save()

        return HttpResponseRedirect(f"/coming_order/{order_id}")

@login_required(login_url="/login/")
def store_coming_info(request, store_id):
    if request.method == 'GET':
        store = get_object_or_404(Customer, id=store_id, is_shop=True)
        arranged_orders = {}
        orders = store.coming_orders.all().order_by('-created_at')

        if not orders:
            return render(request, "main/store_coming_info.html", {
            "store": store,
        })

        rest_orders = orders.filter(is_fully_paid=False)
        total_money_orders = orders.values_list('total_order_price', flat=True)
        rest_money_orders = rest_orders.values_list('rest_money', flat=True)
        total_money = sum(price for price in total_money_orders)
        rest_money = sum(price for price in rest_money_orders)

        total_orders_info = {
                "count": total_money_orders.count(),
                "total_orders": orders,
                "total_money": total_money
                }

        rest_info = {
        "count": rest_money_orders.count(),
        "rest_orders": rest_orders,
        "rest_money": rest_money
        }



        for order in orders:
            order_time = change_zone(order.created_at)

            y = order_time.strftime("%y")
            m = order_time.strftime("%m")
            d = order_time.strftime("%d")
            if str(y) not in arranged_orders.keys():
                arranged_orders[f"{y}"] = {}
            if str(m) not in arranged_orders[f"{y}"].keys():
                arranged_orders[f"{y}"][f"{m}"] = {}
            if str(d) not in arranged_orders[f"{y}"][f"{m}"].keys():
                arranged_orders[f"{y}"][f"{m}"][f"{d}"] = []
            arranged_orders[f"{y}"][f"{m}"][f"{d}"].append(order)



        if total_orders_info and rest_info and total_money:
            percent = (total_money - rest_info["rest_money"]) / total_money * 100
        elif total_orders_info and not rest_info:
            percent = 100

        return render(request, "main/store_coming_info.html", {
            "store": store,
            "orders": orders,
            "arranged_orders": arranged_orders,
            "total_orders_info": total_orders_info,
            "rest_info": rest_info,
            "percent": int(percent),
        })

@login_required(login_url="/login/")
def supplier_coming_info(request, supplier_id):
    if request.method == 'GET':
        supplier = get_object_or_404(Customer, id=supplier_id, is_supplier=True)

        arranged_orders = {}
        orders = supplier.supplier_orders.all().order_by('-created_at')

        if not orders:
            return render(request, "main/supplier_coming_orders.html", {
            "supplier": supplier,
        })
        rest_orders = orders.filter(is_fully_paid=False)
        total_money_orders = orders.values_list('total_order_price', flat=True)
        rest_money_orders = rest_orders.values_list('rest_money', flat=True)
        total_money = sum(price for price in total_money_orders)
        rest_money = sum(price for price in rest_money_orders)

        total_orders_info = {
                "count": total_money_orders.count(),
                "total_orders": orders,
                "total_money": total_money
                }

        rest_info = {
        "count": rest_money_orders.count(),
        "rest_orders": rest_orders,
        "rest_money": rest_money
        }



        for order in orders:
            order_time = change_zone(order.created_at)

            y = order_time.strftime("%y")
            m = order_time.strftime("%m")
            d = order_time.strftime("%d")
            if str(y) not in arranged_orders.keys():
                arranged_orders[f"{y}"] = {}
            if str(m) not in arranged_orders[f"{y}"].keys():
                arranged_orders[f"{y}"][f"{m}"] = {}
            if str(d) not in arranged_orders[f"{y}"][f"{m}"].keys():
                arranged_orders[f"{y}"][f"{m}"][f"{d}"] = []
            arranged_orders[f"{y}"][f"{m}"][f"{d}"].append(order)



        if total_orders_info and rest_info and total_money:
            percent = (total_money - rest_info["rest_money"]) / total_money * 100
        elif total_orders_info and not rest_info:
            percent = 100

        return render(request, "main/supplier_coming_orders.html", {
            "supplier": supplier,
            "orders": orders,
            "arranged_orders": arranged_orders,
            "total_orders_info": total_orders_info,
            "rest_info": rest_info,
            "percent": int(percent),
        })

@login_required(login_url="/login/")
def all_rest_orders(request):
    orders = {}
    customers = Customer.objects.all().order_by('-is_shop', '-name')
    for customer in customers:
        customer_rest = customer.orders.filter(is_fully_paid=False).order_by('created_at')
        if customer_rest.count() > 0:
            orders[customer] = customer_rest
    return render(request, "main/all_rest_orders.html", {
        "orders":orders,
    })

@login_required(login_url="/login/")
def all_rest_coming_orders(request):
    orders = {}
    customers = Customer.objects.filter(is_shop=True).order_by('-name')
    for customer in customers:
        customer_rest = customer.coming_orders.filter(is_fully_paid=False).order_by('created_at')
        if customer_rest.count() > 0:
            orders[customer] = customer_rest
    return render(request, "main/all_rest_orders.html", {
        "orders":orders,
        "coming": True,
    })

############# ############# ############# ############# sales ############# ############# ############# 
@login_required(login_url="/login/")
def month_sales(request):
    arabic_months = {
        1: "يناير",
        2: "فبراير",
        3: "مارس",
        4: "أبريل",
        5: "مايو",
        6: "يونيو",
        7: "يوليو",
        8: "أغسطس",
        9: "سبتمبر",
        10: "أكتوبر",
        11: "نوفمبر",
        12: "ديسمبر"
    }

    try:
        year = int(request.GET.get("y"))
        month = int(request.GET.get("m"))
        month_data = get_totalsales_formonth(year, month)
        shahr = arabic_months.get(month, None)
        # return JsonResponse('month_data)
    except ValueError:
        return HttpResponse("error: خطأ في ادخال الشهر او السنة.")

    month_char_data = {
        "مبيعات الشهر": month_data["orders_sales"],
        "لم يتم سداده بعد": month_data["debt"],
        "مصاريف طلبيات": month_data["coming_sales"],
        }
    debt_char_data = {
        "الربح": month_data["profit"],
        "مستحق للطلبيات": month_data["coming_debt"],
        }
    return render(request, "main/month_sales.html", {
        "month_data": month_data,
        "shahr": shahr,
        "year": year,
        "debt_char_data": debt_char_data,
        "month_char_data": month_char_data,
    })


@login_required(login_url="/login/")
def total_orders(request):
    if request.method == 'GET':
        
        all_orders = Order.objects.filter(is_used=True).order_by("created_at"); all_duration = {}; years_info = {}
        all_coming_date = Store_Order.objects.all().order_by("created_at").values_list('created_at', flat=True)
        for order in all_orders:
            order_time = change_zone(order.created_at)

            if not str(order_time.year) in all_duration.keys():
                all_duration[f"{order_time.year}"] = {}
            if not str(order_time.month) in all_duration[f"{order_time.year}"].keys():
                all_duration[f"{order_time.year}"][f"{order_time.month}"] = get_totalsales_formonth(order.created_at.year, order.created_at.month)

        years_sales = {}; years_profit = {}; years_averages = {}
        for year in all_duration.keys():
            year = int(year)
            years_info[f"{year}"] = get_sales_per_year(year, all_duration[f"{year}"].keys())
            year_order = Order.objects.filter(created_at__range=(datetime.date(year, 1, 1), datetime.date(year + 1, 1, 1)) , is_used=True)
            year_count = year_order.count()
            years_sales[year] = sum(order_price for order_price in year_order.values_list("total_order_price", flat=True))
            years_profit[year] = sum(order_price for order_price in year_order.values_list("profit", flat=True))
            years_averages[year] = round(years_sales[year] / year_count, 2)

        years_info = dict(sorted(years_info.items(), key=lambda x: int(x[0]), reverse=True))


        order_count = all_orders.count() #         اجمالي العدد
        orders_sales = sum(order_price for order_price in all_orders.values_list("total_order_price", flat=True))  #         اجمالي مبيعات
        average_order = round(orders_sales / order_count, 2) #         متوسط سعر الطلب
        total_profits = all_orders.values_list("profit", flat=True)
        total_profit = sum(profit for profit in total_profits)  #         اجمالي ربح
        rest_moneys = all_orders.values_list("rest_money", flat=True)
        rest_money = sum(rest for rest in rest_moneys)  #         اجمالي مستحق
        #########################        ربح كل شهر         #########################

            


        all_data = {
            "order_count": order_count,
            "orders_sales": orders_sales,
            "average_order": average_order,
            "total_profit": total_profit,
            "rest_money": rest_money,
            "years_sales": years_sales,
            "years_profit": years_profit,
            "years_averages": years_averages,
        }
        
        return render(request, "main/sales.html", {
            "years_info": years_info,
            "all_data": all_data,
        })




def get_sales_per_year(year, months):
    orders = Order.objects.filter(created_at__range=(datetime.date(year, 1, 1), datetime.date(year + 1, 1, 1)), is_used=True).order_by("created_at")
    coming_orders = Store_Order.objects.filter(created_at__range=(datetime.date(year, 1, 1), datetime.date(year + 1, 1, 1)))
    order_count = orders.count() #         اجمالي العدد

    orders_sales = sum(orders.values_list("total_order_price", flat=True))  #         اجمالي مبيعات
    coming_sales = sum(coming_orders.values_list("total_order_price", flat=True))  #         اجمالي مبيعات
    average_order = round(orders_sales / order_count, 2) #         متوسط سعر الطلب
    profit = sum(orders.values_list("profit", flat=True))  #         اجمالي ربح
    debt = sum(orders.values_list("rest_money", flat=True))  #         اجمالي ربح
    coming_debt = sum(coming_orders.values_list("rest_money", flat=True))


    #########################        ربح كل شهر         #########################
    months_sales = {}
    for month in months:
        months_sales[month] = (get_totalsales_formonth(year, int(month)))
    ##############################################################################

    year_result = {
        "order_count": order_count, 
        "orders_sales": orders_sales, 
        "profit": profit, 
        "debt": debt, 
        "average_order": average_order,
        "orders": orders,
        "months_sales": months_sales, 
        "months": months, 
        "coming_sales": coming_sales, 
        "coming_debt": coming_debt, 
        }
    return year_result



def get_totalsales_formonth(year, month):
    start_date = datetime.date(year , month, 1)

    if month == 12:
        end_date = datetime.date(year + 1, 1, 1)
    else:
        end_date = datetime.date(year, month + 1, 1)

    orders = Order.objects.filter(created_at__range=(start_date, end_date))
    coming_orders = Store_Order.objects.filter(created_at__range=(start_date, end_date))

    debt = sum(orders.values_list("rest_money", flat=True))
    coming_debt = sum(coming_orders.values_list("rest_money", flat=True))
    coming_sales = sum(coming_orders.values_list("total_order_price", flat=True))
    orders_sales = sum(orders.values_list("total_order_price", flat=True))
    profit = sum(orders.values_list("profit", flat=True)) 
    order_count = orders.count()
    try:
        average_order = round(orders_sales / order_count, 2)
    except ZeroDivisionError:
        average_order = 0

    month_result = {
        "order_count": order_count, 
        "orders_sales": orders_sales, 
        "profit": profit, 
        "average_order": average_order,
        "orders": orders,
        "coming_orders": coming_orders,
        "debt": debt,
        "coming_debt": coming_debt,
        "coming_sales": coming_sales,
        }
    return month_result

############# ############# ############# ############# end_sales ############# ############# ############# 

#################################################################################

def update_items():
    items = Item.objects.all()
    for item in items:
        item.update_item()

def get_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return None
    return order

def get_coming_order(order_id):
    try:
        order = Store_Order.objects.get(id=order_id)
    except Store_Order.DoesNotExist:
        return None
    return order

    
    
def update_discount(order, new_discount):

    order.discount = new_discount
    order.save()
    order.update_same_disc()

def get_rest_info(customer):
    rest_orders = Order.objects.filter(customer=customer, is_fully_paid=False, is_used=True)
    rest_money_orders = rest_orders.values_list('rest_money', flat=True)
    if rest_money_orders.count() != 0:
        return {
            "count": rest_money_orders.count(),
            "rest_orders": rest_orders,
            "rest_money": sum(price for price in rest_money_orders)
            }
        
def get_total_orders_info(customer, year):

    if year == 0:
        total_money_orders = Order.objects.filter(customer=customer, is_used=True).values_list('total_order_price', flat=True)
        total_money = sum(price for price in total_money_orders)
        if total_money > 0:
            return sum(price for price in total_money_orders)

    else:
        if year == "all":
            total_orders = Order.objects.filter(customer=customer, is_used=True)
        else:  
            total_orders = Order.objects.filter(customer=customer, created_at__range=(datetime.date(year, 1, 1), datetime.date(year + 1, 1, 1)), is_used=True)
        total_money_orders = total_orders.values_list('total_order_price', flat=True)
        if total_money_orders.count() != 0:
            return {
                "count": total_money_orders.count(),
                "total_orders": total_orders,
                "total_money": sum(price for price in total_money_orders)
                }
    return None

def change_zone(date):
    return timezone.localtime(date)