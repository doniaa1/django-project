import hashlib
import jwt
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

def md5_hash(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def create_jwt_token(user_id: int, *, exp_seconds=300, username: str = None):
    
    now_dt = timezone.now()
    exp_dt = now_dt + timedelta(seconds=int(exp_seconds))

    payload = {
        "user_id": int(user_id),
        "iat": int(now_dt.timestamp()),
        "exp": int(exp_dt.timestamp()),
    }

    if username:
        payload["username"] = username

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm="HS256")
    

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token, exp_dt, int(exp_dt.timestamp())


def update_jwt_token(user_id, exp_seconds=300, update_existing_token=None, username=None):
   
    now_dt = timezone.now()
    exp_dt = now_dt + timedelta(seconds=exp_seconds)

    payload = {
        "user_id": int(user_id),
        "iat": int(now_dt.timestamp()),
        "exp": int(exp_dt.timestamp()),
    }

    if username:
        payload["username"] = username

    token_str = jwt.encode(
        payload,
        settings.JWT_SECRET,  
        algorithm= "HS256"
    )

    if isinstance(token_str, bytes):
        token_str = token_str.decode("utf-8")

    if update_existing_token:
        update_existing_token.token = token_str
        update_existing_token.exp = exp_dt
        update_existing_token.save()

    return token_str, exp_dt, payload
