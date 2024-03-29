from django.contrib import admin
from tweets.models import Tweet, TweetPhoto


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'user',
        'created_at',
        'updated_at',
    )


@admin.register(TweetPhoto)
class TweetPhotoAdmin(admin.ModelAdmin):
    list_display = (
        'tweet',
        'user',
        'file',
        'status',
        'has_deleted',
        'created_at',
    )
    list_filter = ('status', 'has_deleted')
    data_hierarchy = 'created_at'
