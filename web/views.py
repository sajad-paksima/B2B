from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Token, Profile, Charge, Sell
from django.http import JsonResponse, HttpResponse, HttpRequest, Http404
from json import JSONEncoder
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import ValidationError
import string
import random
from decimal import *
from datetime import datetime
from django.db import transaction

random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

# Create your views here.
@csrf_exempt
def register(request):
    try:
        if User.objects.filter(username=request.POST['username']).exists():
            return JsonResponse({
                "message": "duplicate username!"
            }, encoder=JSONEncoder, status=409)
        else:
            password = make_password(request.POST['password'])
            username = request.POST['username']
            newuser = User.objects.create(username=username, password=password)
            this_token = random_str(48)
            Token.objects.create(user=newuser, token=this_token)
            return JsonResponse({
                "token": this_token,
                "message": "successfully registered!"
            }, encoder=JSONEncoder)
    except Exception as e:
        return handle_exception(e)


@csrf_exempt
def submit_charge(request):
    try:
        this_token = request.POST["token"]
        if this_token != "test":
            return JsonResponse({
                "message": "This user is not allowed to charge!"
            }, encoder=JSONEncoder, status=401)
        else:
            now = datetime.now()
            amount = Decimal(request.POST["amount"])
            username = request.POST["receiver"]
            with transaction.atomic():
                receiver = get_object_or_404(User.objects.select_for_update(), username=username)
                receiver.profile.credit += amount
                receiver.save()
                Charge.objects.create(date=now, amount=amount, receiver=receiver)
            return JsonResponse({
                "message": "The receiver has charged successfully!"
            }, encoder=JSONEncoder, status=200)
    except Exception as e:
        print(e)
        return handle_exception(e)


@csrf_exempt
def submit_sell(request):
    try:
        this_token = request.POST["token"]
        amount = Decimal(request.POST["amount"])
        date = datetime.now()
        phone_number = request.POST["phone_number"]
        with transaction.atomic():
            seller = get_object_or_404(User.objects.select_for_update(), token__token=this_token)
            seller.profile.credit -= amount
            seller.save()
            Sell.objects.create(phone_number=phone_number, date=date, amount=amount, seller=seller)
        return JsonResponse({
            "message": "The seller has sold successfully!"
        }, encoder=JSONEncoder, status=200)
    except Exception as e:
        return handle_exception(e)

def handle_exception(e):
    if isinstance(e, ValidationError):
        response = JsonResponse(e.message_dict, encoder=JSONEncoder, status=422)
    else:
        response = JsonResponse({
            "message": str(e)
        }, encoder=JSONEncoder, status=400)
    if isinstance(e, Http404):
        response.status_code = 404
    return response

