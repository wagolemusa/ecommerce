# Generated by Django 2.0.13 on 2020-04-09 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0017_order_mpesa_pay'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(default=1, upload_to=''),
            preserve_default=False,
        ),
    ]