# Generated by Django 4.2.1 on 2023-07-07 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0027_artwork_number_of_sales'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='e_mail',
            field=models.EmailField(default='', max_length=250, unique=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_num',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]
