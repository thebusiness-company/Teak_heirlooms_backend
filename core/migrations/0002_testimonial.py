# Generated by Django 5.1.6 on 2025-02-27 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='testimonials/')),
                ('title', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('name', models.CharField(max_length=100)),
                ('rating', models.IntegerField(default=5)),
            ],
        ),
    ]
