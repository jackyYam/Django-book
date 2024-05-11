# Generated by Django 5.0.6 on 2024-05-11 15:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0004_book_creator'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='favourites',
            field=models.ManyToManyField(blank=True, related_name='favourite_books', to=settings.AUTH_USER_MODEL),
        ),
    ]
