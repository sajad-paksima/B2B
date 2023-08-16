from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

def validate_non_negative(value):
    if value < 0:
        raise ValidationError(
            message='%(value)s is negative',
            params={'value': value},
        )

def validate_positive(value):
    if value <= 0:
        raise ValidationError(
            message='%(value)s is not positive',
            params={'value': value},
        )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit = models.DecimalField(validators=[validate_non_negative], default=0, max_digits=13, decimal_places=1)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.user}-{self.credit}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Token(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=48)
    def __str__(self):
        return f"{self.user}-token"

class Sell(models.Model):
    phone_regex = RegexValidator(regex=r'^((\+98)|0)\d{10}$',
                                 message="Phone number must be entered in the format: '+989133333333' or '09133333333'.")
    phone_number = models.CharField(validators=[phone_regex], max_length=14)  # Validators should be a list
    date = models.DateTimeField()
    amount = models.DecimalField(validators=[validate_positive], default=0, max_digits=13, decimal_places=1)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.seller}-{self.amount}"

class Charge(models.Model):
    date = models.DateTimeField()
    amount = models.DecimalField(validators=[validate_positive], default=0, max_digits=13, decimal_places=1)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.receiver}-{self.amount}"