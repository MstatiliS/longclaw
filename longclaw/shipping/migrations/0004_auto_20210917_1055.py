# Generated by Django 3.2.7 on 2021-09-17 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0003_auto_20190322_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='shippingrate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='shippingrateprocessor',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]