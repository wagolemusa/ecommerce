# Generated by Django 2.0.13 on 2020-04-09 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0018_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
