from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer
from django.conf import settings


class RedisHelper(object):

    @classmethod
    def _load_objects_to_cache(cls, key, queryset):
        conn = RedisClient.get_connection()

        serialized_list = [
            # 最多只 cache REDIS_LIST_LENGTH_LIMIT 个 objects。
            # 超过这个限制的 objects，就去数据库里读取。
            DjangoModelSerializer.serialize(obj) for obj in queryset[:settings.REDIS_LIST_LENGTH_LIMIT]
        ]

        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()

        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            return [DjangoModelSerializer.deserialize(item) for item in serialized_list]

        cls._load_objects_to_cache(key, queryset)

        return list(queryset)

    @classmethod
    def push_object(cls, key, obj, queryset):
        conn = RedisClient.get_connection()

        if not conn.exists(key):
            # 如果 key 不存在，直接从数据库里 load
            # 就不走单个 push 的方式加到 cache 里了
            cls._load_objects_to_cache(key, queryset)
            return

        serialized_obj = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_obj)
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)

