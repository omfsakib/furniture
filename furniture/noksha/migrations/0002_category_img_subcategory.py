# Generated by Django 4.0.3 on 2022-12-25 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('noksha', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='img',
            field=models.ImageField(blank=True, default='product-pic.jpg', null=True, upload_to=''),
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('img', models.ImageField(blank=True, default='product-pic.jpg', null=True, upload_to='')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='noksha.category')),
            ],
        ),
    ]
