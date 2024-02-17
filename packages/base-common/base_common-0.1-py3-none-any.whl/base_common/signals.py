from django.conf import settings


def process_user_attributes(sender, user, created, attributes, *args, **kwargs):
    if not user:
        return

    if user.username in settings.SUPERUSERS:
        user.is_staff = True
        user.is_superuser = True
        user.save()
    else:
        user.is_staff = False
        user.is_superuser = False
        user.save()
