import logging
from django.apps import apps
from users.models import Token
from django.utils import timezone
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .my_help import JsonResponseUnauthorized  
import jwt
import json


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # عناوين المسارات التي لا تحتاج إلى توثيق (احرص أن تضعها بالشكل الصحيح في مشروعك)
        self.allowed_urls = [
            "/api/login/",
            "/api/register",
            "/api/user/refresh",
            
            "/api/otp/request/",
            "/api/otp/verify/",
            
            "/api/merchant/add-merchant/",
            "/api/pos/return-pos/",
            "/api/pos/order-pos/",
            "/api/pos/getall-pos/",
            "/api/pos/getposbank/",
            "/api/sys-order/get-form-data/",
            "/api/pos/delivery-pos-by-bank/",
            "/api/city/create/",
            "/api/country/create/",
            "/api/country/update/",
            "/api/region/create/",
            "/api/merchant/update-merchant/",
            "/api/merchant/end-contract/",
            "/api/merchant/different/",
            "/api/files/file-merchant-npg/",
            "/api/pos/order-inv/",
            "/api/sop/generate/",
            "/api/sys-order/add-pos/",
            "/api/files/file-merchant-by-bank/",
            "/media/order/",
        ]

    def __call__(self, request):
        try:
            # إذا كان المسار في القائمة المسموحة، نمرر الطلب مباشرة
            for url in self.allowed_urls:
                if request.path.startswith(url):
                    return self.get_response(request)

            # قراءة الـ Authorization header
            token_header = request.META.get("HTTP_AUTHORIZATION")
            if not token_header:
                return JsonResponseUnauthorized("7")  # رمز خطأ مثال

            # دعم صيغة "Bearer <token>"
            if token_header.lower().startswith("bearer "):
                token_str = token_header[7:].strip()
            else:
                token_str = token_header.strip()

            # إيجاد التوكن في قاعدة البيانات
            token = Token.objects.filter(token=token_str).first()
            if token is None:
                return JsonResponseUnauthorized("8")

            # تحقق من انتهاء الصلاحية
            if token.expired_at and token.expired_at < timezone.now():
                token.delete()
                return JsonResponseUnauthorized("9")

            # تمديد وقت الانتهاء إن وُجد إعداد TOKEN_LIFETIME (يفترض أنه timedelta)
            lifetime = None
            try:
                lifetime = settings.AUTH.get("TOKEN_LIFETIME")
            except Exception:
                lifetime = getattr(settings, "TOKEN_LIFETIME", None)

            if lifetime:
                token.expired_at = timezone.now() + lifetime

            # فك التوكن (JWT) واستخراج بيانات المستخدم
            try:
                decoded = jwt.decode(token_str, settings.JWT_SECRET, algorithms=["HS256"])
                request.user_id = decoded.get("user_id")
                request.city_id = decoded.get("city")
            except jwt.InvalidTokenError:
                return JsonResponseUnauthorized("10")

            token.save(update_fields=["expired_at"])

            response = self.get_response(request)
            response["Access-Control-Allow-Origin"] = "*"
            return response

        except Exception as e:
            logging.error("AuthMiddleware error: %s", e, exc_info=True)
            return JsonResponseUnauthorized("6")
