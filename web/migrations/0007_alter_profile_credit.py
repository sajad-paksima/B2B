# Generated by Django 4.2.4 on 2023-08-15 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0006_rename_credit_charge_profile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="credit",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]