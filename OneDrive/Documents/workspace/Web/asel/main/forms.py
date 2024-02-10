from django import forms
from .models import Item, Category, Customer

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['category', 'name', 'real_price', 'gomla_price', 'market_price', 'stock_quantity']
        
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs['class'] = 'form-select'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['real_price'].widget.attrs['class'] = 'form-control'
        self.fields['gomla_price'].widget.attrs['class'] = 'form-control'
        self.fields['market_price'].widget.attrs['class'] = 'form-control'
        self.fields['stock_quantity'].widget.attrs['class'] = 'form-control'
        self.fields['real_price'].widget.attrs['min'] = '0.00'
        self.fields['gomla_price'].widget.attrs['min'] = '0.00'
        self.fields['market_price'].widget.attrs['min'] = '0.00'
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        
        
        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'number', 'is_supplier']

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['number'].widget.attrs['class'] = 'form-control'
        self.fields['is_supplier'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_supplier'].widget.attrs['style'] = 'width: 45px; height: 22px;'
        self.fields['number'].widget.attrs['min'] = '1000000001'
        self.fields['number'].widget.attrs['max'] = '1599999999'
