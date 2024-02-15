from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User
from friendships.services import FriendshipsService
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from utils.paginations import EndlessPagination
from gatekeeper.models import GateKeeper
from friendships.hbase_models import HBaseFollowing, HBaseFollower


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate

    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是
    # queryset.filter(pk=1) 查询一下这个 object 在不在
    queryset = User.objects.all()

    pagination_class = EndlessPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        # GET /api/friendships/1/followers/
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollower, (pk,), request)
        else:
            friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followings(self, request, pk):
        # GET /api/friendships/1/followings/
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollowing, (pk,), request)
        else:
            friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request, pk):
        # check if user with id=pk exists
        to_follow_user = self.get_object()

        if FriendshipsService.has_followed(request.user.id, to_follow_user.id):
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': to_follow_user.id,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        FriendshipsService.invalidate_following_cache(request.user.id)
        return Response(
            FollowingSerializer(instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()  # make sure the user exists
        # 注意 pk 的类型是 str，所以要做类型转换
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = FriendshipsService.unfollow(request.user.id, unfollow_user.id)

        FriendshipsService.invalidate_following_cache(request.user.id)
        return Response({'success': True, 'deleted': deleted})

    def list(self, request):
        return Response({'message': 'this is friendships home page'})