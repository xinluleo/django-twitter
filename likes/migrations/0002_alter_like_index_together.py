# Generated by Django 3.2.9 on 2023-12-20 05:21

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('likes', '0001_initial'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='like',
            index_together={('content_type', 'object_id', 'created_at'), ('user', 'content_type', 'created_at')},
        ),
    ]
