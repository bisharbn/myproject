# hello/utils.py
from hello.models import LoginAudit
import geoip2.database
from django.conf import settings


def create_login_audit(user, request):
    ip = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    device = parse_device(user_agent)

    LoginAudit.objects.create(
        user=user,
        ip_address=ip,
        location = get_location(ip),
        device=device,
        user_agent=user_agent
    )

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')

def parse_device(user_agent):
    if 'Mobile' in user_agent:
        return "Mobile"
    elif 'Tablet' in user_agent:
        return "Tablet"
    else:
        return "Desktop"


def get_location(ip):
    try:
        reader = geoip2.database.Reader(settings.GEOIP_PATH / "GeoLite2-City.mmdb")
        response = reader.city(ip)
        city = response.city.name or "Unknown"
        country = response.country.name or "Unknown"
        reader.close()
        return f"{city}, {country}"
    except Exception:
        return "Unknown"