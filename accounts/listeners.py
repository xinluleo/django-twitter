def profile_changed(sender, instance, **kwargs):
    from accounts.services import UserService
    UserService.invalidate_profile_cache(instance.user_id)
