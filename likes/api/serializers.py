from twitter.accounts.api.serializers import UserSerializer
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Like
        fields = ('user', 'created_at')


class LikeSerializerForCreate(serializers.ModelSerializer):
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

    def create(self, validated_data):
        model_class = self._get_model_class(validated_data['content_type'])
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['request'].user,
        )
        return instance
