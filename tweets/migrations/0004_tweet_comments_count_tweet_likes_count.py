# Generated by Django 5.0.1 on 2024-02-04 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0003_tweetphoto'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='comments_count',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='likes_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
