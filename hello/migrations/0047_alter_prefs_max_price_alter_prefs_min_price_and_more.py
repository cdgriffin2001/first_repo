# Generated by Django 4.2.1 on 2023-07-26 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0046_prefs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prefs',
            name='max_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=50, null=True),
        ),
        migrations.AlterField(
            model_name='prefs',
            name='min_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=50, null=True),
        ),
        migrations.AlterField(
            model_name='prefs',
            name='percent_growth',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=50, null=True),
        ),
        migrations.AlterField(
            model_name='prefs',
            name='time_frame',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
