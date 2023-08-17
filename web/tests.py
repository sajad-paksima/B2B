from django.test import TestCase
from django.urls import reverse

from .models import *

# Create your tests here.

class RegisterTests(TestCase):
    def setUp(self):
        User.objects.create(username="sajad", password="test")
    def test_register(self):
        response = self.client.post(reverse("register"), {
            "username": "Alireza",
            "password": "test"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="Alireza").exists(), True)
        self.assertEqual(Token.objects.filter(user=User.objects.get(username="Alireza")).exists(), True)
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 0)

    def test_register_duplicate(self):
        response = self.client.post(reverse("register"), {
            "username": "sajad",
            "password": "test"
        })
        self.assertEqual(response.status_code, 409)
        self.assertEqual(User.objects.filter(username="sajad").count(), 1)


class SubmitChargeTests(TestCase):
    def setUp(self):
        User.objects.create(username="sajad", password="test")
        User.objects.create(username="Alireza", password="test")
        Token.objects.create(user=User.objects.get(username="sajad"), token="test")

    def test_charge(self):
        response = self.client.post(reverse("submit_charge"), {
            "token": "test",
            "amount": "1000",
            "receiver": "Alireza"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Charge.objects.filter(receiver=User.objects.get(username="Alireza"), amount=1000).exists())
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 1000)

    def test_charge_unauthorized(self):
        response = self.client.post(reverse("submit_charge"), {
            "token": "test1",
            "amount": "1000",
            "receiver": "Alireza"
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 0)

    def test_charge_not_found(self):
        response = self.client.post(reverse("submit_charge"), {
            "token": "test",
            "amount": "1000",
            "receiver": "Sara"
        })
        self.assertEqual(response.status_code, 404)
        self.assertFalse(User.objects.filter(username="Alireza1").exists())

class SubmitSellTests(TestCase):
    def setUp(self):
        User.objects.create(username="sajad", password="test")
        alireza = User.objects.create(username="Alireza", password="test")
        alireza.profile.credit = 10000
        alireza.save()
        Token.objects.create(user=User.objects.get(username="sajad"), token="test")
        Token.objects.create(user=User.objects.get(username="Alireza"), token="test1")

    def test_sell(self):
        response = self.client.post(reverse("submit_sell"), {
            "token": "test1",
            "amount": "1000",
            "phone_number": "09123456789"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Sell.objects.filter(seller=User.objects.get(username="Alireza"), amount=1000).exists())
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 9000)

    def test_sell_validation_error(self):
        response = self.client.post(reverse("submit_sell"), {
            "token": "test1",
            "amount": "1000",
            "phone_number": "091234567892"
        })
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Sell.objects.filter(seller=User.objects.get(username="Alireza"), amount=1000).exists())
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 10000)

    def test_sell_not_found(self):
        response = self.client.post(reverse("submit_sell"), {
            "token": "test2",
            "amount": "1000",
            "phone_number": "09123456789"
        })
        self.assertEqual(response.status_code, 404)
        self.assertFalse(User.objects.filter(token__token="test2").exists())

    def test_sell_not_enough_credit(self):
        response = self.client.post(reverse("submit_sell"), {
            "token": "test1",
            "amount": "20000",
            "phone_number": "09123456789"
        })
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Sell.objects.filter(seller=User.objects.get(username="Alireza"), amount=20000).exists())
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 10000)

class IntegriationTests(TestCase):
    def setUp(self):
        User.objects.create(username="sajad", password="test")
        Token.objects.create(user=User.objects.get(username="sajad"), token="test")

    def test_register_charge_sell(self):
        # register 2 users
        register_response_1 = self.client.post(reverse("register"), {
            "username": "Alireza",
            "password": "test"
        })
        self.assertEqual(register_response_1.status_code, 200)
        self.assertEqual(User.objects.filter(username="Alireza").exists(), True)
        self.assertEqual(Token.objects.filter(user=User.objects.get(username="Alireza")).exists(), True)
        register_response_2 = self.client.post(reverse("register"), {
            "username": "Sara",
            "password": "test"
        })
        self.assertEqual(register_response_2.status_code, 200)
        self.assertEqual(User.objects.filter(username="Sara").exists(), True)
        self.assertEqual(Token.objects.filter(user=User.objects.get(username="Sara")).exists(), True)
        self.assertEqual(User.objects.filter(username__in=["Sara", "Alireza"]).count(), 2)
        # charge each user 10 times
        for _ in range(10):
            charge_response_1 = self.client.post(reverse("submit_charge"), {
                "token": "test",
                "amount": "4000",
                "receiver": "Alireza"
            })
            self.assertEqual(charge_response_1.status_code, 200)
            charge_response_2 = self.client.post(reverse("submit_charge"), {
                "token": "test",
                "amount": "3000",
                "receiver": "Sara"
            })
            self.assertEqual(charge_response_2.status_code, 200)
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 40000)
        self.assertEqual(User.objects.get(username="Sara").profile.credit, 30000)
        # sell 1000 times
        alireza_token = Token.objects.get(user=User.objects.get(username="Alireza")).token
        sara_token = Token.objects.get(user=User.objects.get(username="Sara")).token
        for _ in range(1000):
            sell_response_1 = self.client.post(reverse("submit_sell"), {
                "token": alireza_token,
                "amount": "30",
                "phone_number": "09123456789"
            })
            self.assertEqual(sell_response_1.status_code, 200)
            sell_response_2 = self.client.post(reverse("submit_sell"), {
                "token": sara_token,
                "amount": "25",
                "phone_number": "09198765432"
            })
            self.assertEqual(sell_response_2.status_code, 200)
        self.assertEqual(User.objects.get(username="Alireza").profile.credit, 10000)
        self.assertEqual(User.objects.get(username="Sara").profile.credit, 5000)
