# Generated by Django 2.0.13 on 2020-04-16 21:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0026_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='email',
            field=models.EmailField(default=datetime.datetime(2020, 4, 16, 21, 57, 44, 661579, tzinfo=utc), max_length=254),
            preserve_default=False,
        ),
    ]