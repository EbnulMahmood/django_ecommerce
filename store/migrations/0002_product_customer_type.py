# Generated by Django 3.2.4 on 2021-06-11 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='customer_type',
            field=models.CharField(blank=True, choices=[('man', 'man'), ('wonam', 'wonam'), ('kids', 'kids'), ('all', 'all')], max_length=20),
        ),
    ]
