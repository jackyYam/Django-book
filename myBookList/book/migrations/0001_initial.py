# Generated by Django 5.0.6 on 2024-05-10 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('publicationYear', models.IntegerField()),
                ('isbn', models.CharField(max_length=13)),
            ],
        ),
    ]