# Generated by Django 5.1.7 on 2025-03-20 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='amount_collected',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
    ]
