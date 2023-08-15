from django.urls import include, re_path
from . import views

urlpatterns = [
    re_path(r"^accounts/register/$", views.register, name="register"),
    re_path(r"^submit/charge/$", views.submit_charge, name="submit_charge"),
    re_path(r"^submit/sell/$", views.submit_sell, name="submit_sell"),
]