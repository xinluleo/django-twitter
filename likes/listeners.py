from utils.redis_helper import RedisHelper


def incr_likes_count(sender, instance, created, **kwargs):
    if not created:
        return

    from tweets.models import Tweet
    from comments.models import Comment
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class == Tweet:
        Tweet.objects.filter(id=instance.content_object.id).update(likes_count=F('likes_count') + 1)
        RedisHelper.incr_count(instance.content_object, 'likes_count')
    elif model_class == Comment:
        Comment.objects.filter(id=instance.content_object.id).update(likes_count=F('likes_count') + 1)


def decr_likes_count(sender, instance, **kwargs):
    from tweets.models import Tweet
    from comments.models import Comment
    from django.db.models import F

    model_class = instance.content_type.model_class()
    if model_class == Tweet:
        Tweet.objects.filter(id=instance.content_object.id).update(likes_count=F('likes_count') - 1)
        RedisHelper.decr_count(instance.content_object, 'likes_count')
    elif model_class == Comment:
        Comment.objects.filter(id=instance.content_object.id).update(likes_count=F('likes_count') - 1)