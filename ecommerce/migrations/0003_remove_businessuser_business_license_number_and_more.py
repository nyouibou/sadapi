# Generated by Django 5.1.3 on 2024-12-02 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0002_remove_supplierproduct_supplier_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessuser',
            name='business_license_number',
        ),
        migrations.RemoveField(
            model_name='businessuser',
            name='registration_date',
        ),
        migrations.AddField(
            model_name='businessuser',
            name='uploaded_file',
            field=models.FileField(blank=True, null=True, upload_to='business_user_files/'),
        ),
        migrations.AddField(
            model_name='offer',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='offer_images/'),
        ),
    ]