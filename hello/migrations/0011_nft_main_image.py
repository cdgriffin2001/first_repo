# Generated by Django 4.2.1 on 2023-06-22 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0010_rename_is_nft_artwork_has_nft_nft'),
    ]

    operations = [
        migrations.AddField(
            model_name='nft',
            name='main_image',
            field=models.ImageField(default=1, upload_to='nfts/'),
            preserve_default=False,
        ),
    ]
