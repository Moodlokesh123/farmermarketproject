from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Farmer,Buyer,Crop,Order

admin.site.register(Farmer)
admin.site.register(Buyer)
admin.site.register(Crop)
admin.site.register(Order)
