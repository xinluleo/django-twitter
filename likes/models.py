from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from utils.memcached_helper import MemcachedHelper
from django.db.models.signals import post_save, pre_delete
from likes.listeners import incr_likes_count, decr_likes_count


class Like(models.Model):
    object_id = models.PositiveIntegerField()  # comment id or tweet id
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)

    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 这里使用 unique together 也就会建一个 <user, content_type, object_id>
        # 的索引。这个索引同时还可以具备查询某个 user like 了哪些不同的 objects 的功能
        # 因此如果 unique together 改成 <content_type, object_id, user>
        # 就没有这样的效果了
        unique_together = (('user', 'content_type', 'object_id'),)
        # 这个 index 的作用是可以按时间排序某个被 like 的 content_object 的所有 likes
        index_together = (
            ('content_type', 'object_id', 'created_at'),
            ('user', 'content_type', 'created_at'),
        )

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


pre_delete.connect(decr_likes_count, sender=Like)
post_save.connect(incr_likes_count, sender=Like)