# Generated by Django 4.2 on 2023-05-20 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_alter_cart_shipping_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitems',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.address'),
        ),
    ]
