# Generated by Django 4.2.1 on 2023-08-08 00:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0048_userprofile_e_mail_userprofile_phone_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='nft',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='artworkpricehistory',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='pricehistory',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
