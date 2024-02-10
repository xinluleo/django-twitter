from django.conf import settings

import happybase


class HBaseClient:
    connection = None

    @classmethod
    def get_connection(cls):
        if cls.connection is None:
            cls.connection = happybase.Connection(settings.HBASE_HOST)
        return cls.connection