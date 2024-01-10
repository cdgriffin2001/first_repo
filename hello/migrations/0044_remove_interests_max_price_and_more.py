# Generated by Django 4.2.1 on 2023-07-16 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0043_remove_customuser_art_watchlist_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interests',
            name='max_price',
        ),
        migrations.RemoveField(
            model_name='interests',
            name='min_price',
        ),
        migrations.AddField(
            model_name='nft',
            name='nft_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=50),
        ),
    ]
