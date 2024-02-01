from django.core.cache import caches
from django.conf import settings
from accounts.listeners import user_changed, profile_changed
from accounts.models import User, UserProfile
from twitter.cache import USER_PATTERN, USER_PROFILE_PATTERN
from django.db.models.signals import pre_delete, post_save

cache = caches['testing'] if settings.TESTING else caches['default']


class UserService:

    @classmethod
    def get_user_through_cache(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)
        user = cache.get(key)
        if user is None:
            user = User.objects.get(id=user_id)
            cache.set(key, user)
        return user

    @classmethod
    def invalidate_user_cache(cls, user_id):
        cache.delete(USER_PATTERN.format(user_id=user_id))

    @classmethod
    def get_profile_through_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        profile = cache.get(key)
        if profile is None:
            profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
            cache.set(key, profile)
        return profile

    @classmethod
    def invalidate_profile_cache(cls, user_id):
        cache.delete(USER_PROFILE_PATTERN.format(user_id=user_id))


pre_delete.connect(user_changed, sender=User)
post_save.connect(user_changed, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)