import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail

def generate_numeric_otp(length=6):
    start = 10**(length-1)
    end = (10**length)-1
    return str(random.randint(start, end))

def otp_expiry_dt():
    minutes = getattr(settings, "OTP_EXPIRY_MINUTES", 5)
    return timezone.now() + timedelta(minutes=int(minutes))

def send_otp_via_email(email: str, otp_code: str):
  
    subject = "Your verification code"
    message = f"Your verification code is: {otp_code}\nIt expires in {getattr(__import__('django.conf').conf.settings, 'OTP_EXPIRY_MINUTES', 5)} minutes."
    from_email = getattr(__import__('django.conf').conf.settings, "DEFAULT_FROM_EMAIL", None)
    return send_mail(subject, message, from_email, [email], fail_silently=False)
