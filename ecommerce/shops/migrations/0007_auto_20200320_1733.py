# Generated by Django 2.0.13 on 2020-03-20 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0006_auto_20200320_1431'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='ordred',
            new_name='ordered',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='orderd_date',
            new_name='ordered_date',
        ),
    ]
