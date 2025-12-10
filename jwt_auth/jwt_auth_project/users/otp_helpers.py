from django.utils import timezone
from .models import OTPBan, OTP
from django.conf import settings

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def is_banned(email=None, ip=None):
    now = timezone.now()
    qs = OTPBan.objects.filter(banned_until__gt=now)
    if email and qs.filter(email=email).exists():
        return True
    if ip and qs.filter(ip=ip).exists():
        return True
    return False

def create_ban(email=None, ip=None, reason="too_many_attempts"):
    from django.utils import timezone
    from datetime import timedelta
    minutes = getattr(settings, "OTP_BAN_MINUTES", 30)
    until = timezone.now() + timedelta(minutes=int(minutes))
    return OTPBan.objects.create(email=email, ip=ip, banned_until=until, reason=reason)

def last_otp_request_recent(email=None, ip=None):
    """
    تحقق مما إذا تم طلب OTP لنفس الايميل في أقل من OTP_REQUEST_MIN_SECONDS
    """
    from django.utils import timezone
    secs = getattr(settings, "OTP_REQUEST_MIN_SECONDS", 60)
    if not email:
        return False
    recent = OTP.objects.filter(email=email).order_by("-created_at").first()
    if not recent:
        return False
    diff = timezone.now() - recent.created_at
    return diff.total_seconds() < int(secs)
