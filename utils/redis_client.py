from django.conf import settings
import redis


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        if cls.conn is None:
            cls.conn = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
            )
        return cls.conn

    @classmethod
    def clear(cls):
        if not settings.TESTING:
            raise Exception("You can not flush redis in production environment")

        if cls.conn is not None:
            cls.conn.flushdb()