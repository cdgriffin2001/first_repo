# Generated by Django 4.2.1 on 2023-06-22 20:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0009_artwork_is_nft_artwork_is_for_sale_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='artwork',
            old_name='is_NFT',
            new_name='has_NFT',
        ),
        migrations.CreateModel(
            name='NFT',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_for_sale', models.BooleanField(default=False)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='NFT', to='hello.artwork')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='NFTs_owned', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
