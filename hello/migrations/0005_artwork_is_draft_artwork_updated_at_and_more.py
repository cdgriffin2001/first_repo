# Generated by Django 4.2.1 on 2023-06-07 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0004_artworkimage_artwork'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='is_draft',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='artwork',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.RemoveField(
            model_name='artwork',
            name='additional_images',
        ),
        migrations.AlterField(
            model_name='artwork',
            name='main_image',
            field=models.ImageField(upload_to='artworks/'),
        ),
        migrations.AlterField(
            model_name='artwork',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='artwork',
            name='share_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='artwork',
            name='shares_count',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='ArtworkImage',
        ),
        migrations.AddField(
            model_name='artwork',
            name='additional_images',
            field=models.ImageField(blank=True, upload_to='artworks/'),
        ),
    ]
