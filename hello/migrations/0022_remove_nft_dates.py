# Generated by Django 4.2.1 on 2023-07-01 02:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0021_remove_nft_dates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nft',
            name='dates',
        ),
    ]
