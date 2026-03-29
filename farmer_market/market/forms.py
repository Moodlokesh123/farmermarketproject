from django import forms
from .models import Farmer, Buyer, Crop


class FarmerForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['name', 'email', 'password', 'phone']


class BuyerForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ['name', 'email', 'password', 'phone']


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['crop_name', 'price', 'quantity', 'image']