# Generated by Django 5.0.1 on 2024-02-04 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comments_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='likes_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
