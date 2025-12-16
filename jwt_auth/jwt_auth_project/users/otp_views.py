from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.conf import settings

from .models import OTP
from .otp_utils import generate_numeric_otp, otp_expiry_dt, send_otp_via_email
from .otp_helpers import get_client_ip, is_banned, create_ban, last_otp_request_recent
from .otp_serializers import RequestOTPSerializer, VerifyOTPSerializer

MAX_ATTEMPTS = getattr(settings, "MAX_OTP_ATTEMPTS", 4)

@api_view(["POST"])
def request_otp(request):
    ser = RequestOTPSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)
    email = ser.validated_data["email"]
    ip = get_client_ip(request)

    if is_banned(email=email, ip=ip):
        return Response({"detail": "blocked"}, status=status.HTTP_403_FORBIDDEN)

    if last_otp_request_recent(email=email, ip=ip):
        return Response({"detail": "too_many_requests"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    otp_code = generate_numeric_otp(getattr(settings, "OTP_LENGTH", 6))
    otp = OTP(
        email=email,
        expires_at=otp_expiry_dt(),
        last_requested_ip=ip
    )
    otp.set_plain_otp(otp_code)
    otp.save()

    try:
        send_otp_via_email(email, otp_code)
    except Exception as e:
        return Response({"detail": "email_send_failed", "error": str(e)}, status=500)

    return Response({
        "otp_token": str(otp.otp_token),
        "expires_at": otp.expires_at.isoformat()
    }, status=201)


@api_view(["POST"])
def verify_otp(request):
    ser = VerifyOTPSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)
    otp_token = ser.validated_data["otp_token"]
    otp_code = ser.validated_data["otp_code"]
    ip = get_client_ip(request)

    try:
        otp = OTP.objects.get(otp_token=otp_token)
    except OTP.DoesNotExist:
        return Response({"detail": "invalid_token"}, status=400)

    if is_banned(email=otp.email, ip=ip):
        return Response({"detail": "blocked"}, status=403)

    if otp.is_used or otp.expired():
        return Response({"detail": "expired_or_used"}, status=400)

    if otp.check_plain_otp(otp_code):
        otp.is_used = True
        otp.save()
        # هنا: بعد التحقق يمكنك إصدار توكن دخول جديد أو تفعيل المستخدم حسب المطلوب.
        return Response({"detail": "verified"}, status=200)
    else:
        otp.attempts += 1
        otp.save()
        if otp.attempts > MAX_ATTEMPTS:
            create_ban(email=otp.email, ip=ip, reason="too_many_attempts")
            return Response({"detail": "banned"}, status=403)
        return Response({"detail": "invalid_code", "attempts": otp.attempts}, status=400)
