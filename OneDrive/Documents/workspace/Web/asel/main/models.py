from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from pytz import timezone



from django.db import models



class Customer(models.Model):
    name = models.CharField(max_length=64)
    is_shop = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    number = models.PositiveIntegerField(
        unique=True,
        validators=[
            MinValueValidator(1000000001), 
            MaxValueValidator(1599999999)
        ]
    )
    def get_rest(self):
        if self.is_supplier:
            return sum(self.supplier_orders.values_list("rest_money", flat=True))
        else:
            return None

        
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "number": self.number,
        }

    def __str__(self):
        return f"{self.id}: {self.name} ({self.number})"

        

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(null=True, blank=True)
    total_real_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_order_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    discount = models.IntegerField(default = 0, validators=[
            MinValueValidator(-100), 
            MaxValueValidator(100)
        ])
    is_gomla = models.BooleanField(default=False)
    is_used = models.BooleanField(default=True)
    is_fully_paid = models.BooleanField(default=True)
    rest_money = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now(timezone('Egypt'))
        if not self.is_fully_paid and self.rest_money == 0:
            self.is_fully_paid = True
        super().save(*args, **kwargs)

    def get_price(self, name):
        if name == "actual_price":
            if self.is_gomla:
                return sum(item_order.gomla_price for item_order in self.order_items.all()) 
            else:
                return sum(item_order.market_price for item_order in self.order_items.all())

        if name == "total_order_price":
            return self.get_price("actual_price") - self.get_price("discount_price")

        if name == "total_real_price":
            return sum(item_order.real_price for item_order in self.order_items.all())

        if name == "discount_price":
            actual_price = self.get_price("actual_price")
            return actual_price - self.total_order_price

        if name == "discount":
            actual_price = self.get_price("actual_price")
            discount_price = self.get_price("discount_price")
            try:
                return int((discount_price / actual_price) * 100)
            except ZeroDivisionError:
                return 0

    def update_total_prices(self, new_total):
        actual_price = self.get_price("actual_price")
        total_real_price = self.get_price("total_real_price")

        if self.total_order_price != new_total:
            self.total_order_price = new_total
        else:
            self.total_real_price = total_real_price
            self.total_order_price = self.get_price("total_order_price")

        self.actual_price = actual_price

        self.profit = new_total - total_real_price
        self.discount = ((actual_price - new_total) / actual_price) * 100
        self.save()

    def update_same_disc(self):
        actual_price = self.get_price("actual_price")
        new_total_order_price = actual_price / 100 * (100 - self.discount)
        self.total_real_price = self.get_price("total_real_price")
        self.total_order_price = new_total_order_price
        self.actual_price = actual_price
        self.profit = new_total_order_price - self.get_price("total_real_price")
        self.save()


    def __str__(self):
        return f"#{self.id} for {self.customer} ({self.total_real_price}) pound"



class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.name}"
    
class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items", null=True)
    name = models.CharField(max_length=64, unique=True)
    real_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    gomla_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0.00)])
    market_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0.00)])
    stock_quantity = models.PositiveIntegerField(default = 0)
    used_quantity = models.PositiveIntegerField(default = 0)
    quantity = models.PositiveIntegerField(default = 0)

    def update_item(self):
        try:
            order_items = OrderItem.objects.filter(item=self)
            self.used_quantity = 0
            for order_item in order_items:
                self.used_quantity += order_item.quantity
        except :
            self.used_quantity = 0
        
        self.quantity = self.stock_quantity - self.used_quantity

        self.save()
        
    def __str__(self):
        return f"{self.name}: {self.quantity}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_itemss')
    quantity = models.PositiveIntegerField()
    real_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gomla_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    market_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)


    def save(self, *args, **kwargs):
        self.real_price = self.quantity * self.item.real_price

        self.gomla_price = self.quantity * self.item.gomla_price

        self.market_price = self.quantity * self.item.market_price
        if self.order.is_gomla:
            self.profit = self.gomla_price - self.real_price
        else:
            self.profit = self.market_price - self.real_price
            
        super().save(*args, **kwargs)

        # Update the total prices of the associated order
        self.item.update_item()
        self.order.update_same_disc()

    def update_profit(self):
        if self.order.is_gomla:
            self.profit = (self.gomla_price / 100 * (100 - self.order.discount)) - self.real_price
        else:
            self.profit = self.market_price - self.real_price

        self.save()
    def __str__(self):
        return f"{self.quantity} x {self.item} in Order #{self.order.id} - Price: {self.real_price}"


class Store_Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="coming_orders", limit_choices_to={'is_shop': True})
    supplier = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="supplier_orders", limit_choices_to={'is_supplier': True} ,null=True, blank=True)
    created_at = models.DateTimeField()
    total_order_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_fully_paid = models.BooleanField(default=True)
    is_done = models.BooleanField(default=False)

    rest_money = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now(timezone('Egypt'))
        if not self.is_fully_paid and self.rest_money < 1:
            self.is_fully_paid = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        order_items = Store_OrderItem.objects.filter(order=self)
        if order_items:
            for order_item in order_items:
                order_item.delete()
            

        super().delete(*args, **kwargs)



    def __str__(self):
        return f"#{self.id} for {self.customer} ({self.total_order_price}) *{self.rest_money}* pound"

        

class Store_OrderItem(models.Model):
    order = models.ForeignKey(Store_Order, on_delete=models.CASCADE, related_name='order_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()

    total_real_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_gomla_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_market_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    single_real_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    single_gomla_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    single_market_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    change_real_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    change_gomla_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    change_market_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_real_price = self.quantity * self.single_real_price
        self.total_gomla_price = self.quantity * self.single_gomla_price
        self.total_market_price = self.quantity * self.single_market_price

        self.change_real_price = self.single_real_price - self.item.real_price
        self.change_gomla_price = self.single_gomla_price - self.item.gomla_price
        self.change_market_price = self.single_market_price - self.item.market_price

        super().save(*args, **kwargs)

        self.update_item_prices()

    def delete(self, *args, **kwargs):
        self.update_item_prices(reverse=True)
        super().delete(*args, **kwargs)

    def update_item_prices(self, reverse=False):
        if reverse:
            factor = -1
        else:
            factor = 1

        self.item.real_price += factor * self.change_real_price
        self.item.gomla_price += factor * self.change_gomla_price
        self.item.market_price += factor * self.change_market_price
        self.item.stock_quantity += factor * self.quantity
        self.item.save()
        self.item.update_item()

        self.order.total_order_price += factor * self.total_real_price
        self.order.save()

    def __str__(self):
        return f"{self.quantity} x {self.item} in Order #{self.order.id} - Price: {self.total_real_price}"

