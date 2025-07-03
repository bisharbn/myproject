# yourapp/pipeline.py
from .models import UserProfile
from django.utils.timezone import now
import logging
from django.contrib.auth import login as django_login
from django.contrib.auth import get_backends
from hello.utils.audit_utils import create_login_audit

logger = logging.getLogger(__name__)

def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.google_id = response.get('sub')
        profile.profile_pic = response.get('picture')
        profile.email = response.get('email')
        profile.save()

def log_google_login(strategy, details, user=None, *args, **kwargs):
    if user:
        ip = get_client_ip(strategy.request)
        logger.info(f"✅ Google Login: {user.username} from IP {ip} at {now()}")
    return


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# hello/pipeline.py


def force_user_logged_in(strategy, backend, user=None, request=None, **kwargs):
    if user and request:
        if not hasattr(user, 'backend'):
            user.backend = backend.__module__ + "." + backend.__class__.__name__
        django_login(request, user)

        # ✅ log audit directly
        create_login_audit(user, request)