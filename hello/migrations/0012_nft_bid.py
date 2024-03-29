# Generated by Django 4.2.1 on 2023-06-22 21:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0011_nft_main_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='NFT_bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('bid_date', models.DateTimeField(auto_now_add=True)),
                ('NFT', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='hello.nft')),
                ('bidder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
