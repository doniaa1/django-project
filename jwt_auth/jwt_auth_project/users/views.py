from functools import wraps
import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import User, Token, RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from .utils import md5_hash, create_jwt_token



@api_view(["POST"])
def register(request):
    ser = RegisterSerializer(data=request.data)
    if ser.is_valid():
        username = ser.validated_data["username"]
        password = ser.validated_data["password"]
        email = ser.validated_data.get("email")

        if User.objects.filter(username=username).exists():
            return Response({"error": "username exists"}, status=400)

        hashed = md5_hash(password)

        user = User.objects.create(
            username=username,
            email=email,
            password=hashed
        )

        return Response({"message": "user created", "id": user.id})
    return Response(ser.errors, status=400)


@api_view(["POST"])
def login(request):
    print("Login request data:", request.data)
    ser = LoginSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=400)

    username = ser.validated_data["username"]
    password = ser.validated_data["password"]

    hashed = md5_hash(password)

    try:
        user = User.objects.get(username=username, password=hashed)
    except User.DoesNotExist:
        return Response({"error": "invalid credentials"}, status=401)

    token_str, exp_dt, _ = create_jwt_token(user.id,username=user.username,exp_seconds=getattr(settings, "JWT_EXP_SECONDS", 300))

    Token.objects.create(user=user, token=token_str, exp=exp_dt)

    refresh_str = str(uuid.uuid4())
    RefreshToken.objects.create(user=user, token=refresh_str)

    return Response({
        "token": token_str,
        "exp": exp_dt.isoformat(),
        "refresh": refresh_str
    })


@api_view(["POST"])
def refresh_access(request):
   
    refresh = request.data.get("refresh")
    if not refresh:
        return Response({"error": "refresh required"}, status=400)
    try:
        rt = RefreshToken.objects.get(token=refresh, revoked=False)
    except RefreshToken.DoesNotExist:
        return Response({"error": "invalid refresh"}, status=401)

    user = rt.user
    new_token, new_exp_dt, _ = create_jwt_token(user.id,username=user.username, exp_seconds=getattr(settings, "JWT_EXP_SECONDS", 300))
    Token.objects.create(user=user, token=new_token, exp=new_exp_dt)
    return Response({"token": new_token, "exp": new_exp_dt.isoformat()})


@api_view(["GET"])
def protected(request):
    
    # تحقق من انتهاء التوكن
    if getattr(request, "token_expired", False):
        return Response({"error": "token expired"}, status=401)

    # تحقق من وجود مستخدم
    if not getattr(request, "user", None):
        return Response({"error": "token required or invalid"}, status=401)

    # تجهيز الاستجابة
    response = Response({
        "message": f"Welcome {request.user.username}",
        "time": timezone.now().isoformat()
    })

    # إضافة التوكن الجديد في الهيدر إذا تم إنشاؤه
    new_token = getattr(request, "_new_token", None)
    if new_token:
        response["X-New-Token"] = new_token

    return response

