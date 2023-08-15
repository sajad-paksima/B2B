from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Token, Profile, Charge, Sell
from django.http import JsonResponse, HttpResponse, HttpRequest
from json import JSONEncoder
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
import string
import random
from datetime import datetime
from django.db import transaction

random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

# Create your views here.
@csrf_exempt
def register(request):
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

@csrf_exempt
def submit_charge(request):
    this_token = request.POST["token"]
    if this_token != "test":
        return JsonResponse({
            "message": "This user is not allowed to charge!"
        }, encoder=JSONEncoder, status=401)
    else:
        now = datetime.now()
        amount = int(request.POST["amount"])
        username = request.POST["receiver"]
        with transaction.atomic():
            # try:
            # except User.DoesNotExist:
            #     return JsonResponse({
            #         "message": "This user doesn't exist!"
            #     }, encoder=JSONEncoder, status=404)
            # charge = Charge.objects.create(date=now, amount=amount, receiver=receiver)
            receiver = get_object_or_404(User.objects.select_for_update(), username=username)
            Charge.objects.create(date=now, amount=amount, receiver=receiver)
            receiver.profile.credit += amount
            receiver.save()
        return JsonResponse({
            "message": "The receiver has charged successfully!"
        }, encoder=JSONEncoder, status=200)

@csrf_exempt
def submit_sell(request):
    this_token = request.POST["token"]
    amount = int(request.POST["amount"])
    date = datetime.now()
    phone_number = request.POST["phone_number"]
    with transaction.atomic():
        # try:
        # except User.DoesNotExist:
        #     return JsonResponse({
        #         "message": "Seller doesn't exist!"
        #     }, encoder=JSONEncoder, status=404)
        seller = get_object_or_404(User.objects.select_for_update(), token__token=this_token)
        if seller.profile.credit < amount:
            return JsonResponse({
                "message": "Seller credit is not enough!"
            }, encoder=JSONEncoder, status=400)
        Sell.objects.create(phone_number=phone_number, date=date, amount=amount, seller=seller)
        seller.profile.credit -= amount
        seller.save()
    return JsonResponse({
        "message": "The seller has sold successfully!"
    }, encoder=JSONEncoder, status=200)

