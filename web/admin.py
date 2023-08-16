from django.contrib import admin
from .models import Sell, Charge, Token, Profile

# Register your models here.
@admin.register(Sell)
class SellAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "date", "amount", "seller")
    readonly_fields = ("amount", "seller")
@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "receiver")
    readonly_fields = ("amount", "receiver")
@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token")
    readonly_fields = ("token", "user")
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "credit")
    readonly_fields = ("credit",)
