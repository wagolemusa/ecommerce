# Generated by Django 2.0.13 on 2020-04-29 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0003_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='one_click_purchasing',
            field=models.BooleanField(default=False),
        ),
    ]
