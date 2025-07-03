import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.gis.geoip2 import GeoIP2
from .models import LoginAudit

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    location = get_location(ip)
    print(f"🟢 LoginAudit saved for {user.username} from {ip}")
    LoginAudit.objects.create(
        user=user,
        ip_address=ip,
        location=location,
        device=parse_device(user_agent),
        user_agent=user_agent
    )

@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    latest_log = LoginAudit.objects.filter(user=user, logout_time__isnull=True).order_by('-login_time').first()
    if latest_log:
        latest_log.logout_time = now()
        latest_log.save()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    agent = request.META.get("HTTP_USER_AGENT", "")
    device = "Mobile" if "Mobile" in agent else "Desktop"
    
    LoginAudit.objects.create(
        user=user,
        ip_address=ip,
        user_agent=agent,
        device=device,
        location="(to be added later)"
    )


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')

def get_location(ip):
    try:
        g = GeoIP2()
        city = g.city(ip)
        return f"{city.get('city')}, {city.get('country_name')}"
    except:
        return "Unknown"

def parse_device(user_agent):
    if 'Mobile' in user_agent:
        return "Mobile"
    elif 'Tablet' in user_agent:
        return "Tablet"
    else:
        return "Desktop"
