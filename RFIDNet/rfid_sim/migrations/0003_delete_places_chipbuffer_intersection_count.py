# Generated by Django 4.2.7 on 2023-12-17 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rfid_sim', '0002_route'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Places',
        ),
        migrations.AddField(
            model_name='chipbuffer',
            name='intersection_count',
            field=models.IntegerField(null=True),
        ),
    ]