from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from dateutil import parser
from django.conf import settings

class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def to_html(self):
        pass

    def paginate_cached_list(self, cached_list, request):
        paginated_list = self.paginate_ordered_list(cached_list, request)

        # 如果是上翻页，paginated_list 里是所有的最新的数据，直接返回
        if 'created_at__gt' in request.query_params:
            return paginated_list

        # 如果还有下一页，说明 cached_list 里的数据还没有取完，也直接返回
        if self.has_next_page:
            return paginated_list

        # 如果 cached_list 的长度不足最大限制，说明 cached_list 里已经是所有数据了
        if len(cached_list) < settings.REDIS_LIST_LENGTH_LIMIT:
            return paginated_list

        # 如果进入这里，说明可能存在在数据库里没有 load 在 cache 里的数据，需要直接去数据库查询
        return None

    def paginate_ordered_list(self, reverse_ordered_list, request):
        if 'created_at__gt' in request.query_params:
            created_at__gt = parser.isoparse(request.query_params['created_at__gt'])
            objects = []
            for item in reverse_ordered_list:
                if item.created_at > created_at__gt:
                    objects.append(item)
                else:
                    break
            self.has_next_page = False;
            return objects

        index = 0
        if 'created_at__lt' in request.query_params:
            created_at__lt = parser.isoparse(request.query_params['created_at__lt'])
            for index, item in enumerate(reverse_ordered_list):
                if item.created_at < created_at__lt:
                    # 找到第一个 created_at 时间小于 created_at__lt 的 item。
                    # 因为数组是按照 created_at 降序排列的，所以之后的 item 都有更早的 created_at 时间。
                    break
            else:
                # 如果没找到满足条件 created_at__lt 的 item，那么就返回空数组
                reverse_ordered_list = []

        self.has_next_page = len(reverse_ordered_list) > index + self.page_size
        return reverse_ordered_list[index: index + self.page_size]

    def paginate_queryset(self, queryset, request, view=None):
        # Handle tweet cached list case
        if type(queryset) == list:
            return self.paginate_ordered_list(queryset, request)

        if 'created_at__gt' in request.query_params:
            # min_id 用于下拉刷新的时候加载最新的内容进来
            # 为了简便起见，下拉刷新不做翻页机制，直接加载所有更新的数据
            # 因为如果数据很久没有更新的话，不会采用下拉刷新的方式进行更新，而是重新加载最新的数据
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')

        if 'created_at__lt' in request.query_params:
            # max_id 用于上拉加载旧的内容
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
            'results': data,
            'has_next_page': self.has_next_page,
        })
