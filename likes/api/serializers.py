from accounts.api.serializers import UserSerializerForLike
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike()

    class Meta:
        model = Like
        fields = ('user', 'created_at')


class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=['tweet', 'comment'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def _get_model_class(self, content_type):
        if content_type == 'tweet':
            return Tweet
        if content_type == 'comment':
            return Comment
        return None

    def validate(self, data):
        model_class = self._get_model_class(data['content_type'])
        if model_class is None:
            raise ValidationError({
                'content_type': 'Content type does not exist'
            })
        liked_object = model_class.objects.filter(id=data['object_id']).first()
        if not liked_object:
            raise ValidationError({
                'object_id': 'Object does not exist'
            })
        return data


class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):

    def get_or_create(self):
        validated_data = self.validated_data
        model_class = self._get_model_class(validated_data['content_type'])
        return Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['request'].user,
        )


class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):

    def cancel(self):
        """
        cancel 方法是一个自定义的方法，cancel 不会被 serializer.save() 调用
        因为 serializer.save() 只会调用 create 方法
        所以我们要在 view 里面调用 serializer.cancel()
        """
        model_class = self._get_model_class(self.validated_data['content_type'])
        deleted, _ = Like.objects.filter(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['request'].user,
        ).delete()
        return deleted