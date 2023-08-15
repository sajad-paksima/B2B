from django.contrib import admin
from .models import Sell, Charge, Token, Profile

# Register your models here.
admin.site.register(Sell)
admin.site.register(Charge)
admin.site.register(Token)
admin.site.register(Profile)
