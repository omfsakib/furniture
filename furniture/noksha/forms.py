from django.forms import ModelForm
from django import forms
from .models import *

class ProductForm(ModelForm):
    name = forms.CharField(label='Product Name',widget=forms.TextInput(attrs={'placeholder': 'Product Name'}))
    price = forms.FloatField(label='Price',widget=forms.TextInput(attrs={'placeholder': 'Price'}))
    description = forms.CharField(max_length=2000,label='Description',widget=forms.Textarea(attrs={'placeholder': 'Description'}))
    product_code = forms.CharField(max_length=200,label='Product Code',widget=forms.TextInput(attrs={'placeholder': 'Product code'}))
    category = forms.ModelMultipleChoiceField(
            queryset=Category.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True)
    color = forms.ModelMultipleChoiceField(
            queryset=Color.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True)
    size = forms.ModelMultipleChoiceField(
            queryset=Size.objects.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True)
    
    class Meta:
        model = Product
        fields = '__all__'