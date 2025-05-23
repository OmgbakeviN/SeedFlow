# Generated by Django 5.1.3 on 2025-02-27 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('entrepreneur', 'Entrepreneur'), ('investisseur', 'Investisseur')], max_length=20, null=True),
        ),
    ]
