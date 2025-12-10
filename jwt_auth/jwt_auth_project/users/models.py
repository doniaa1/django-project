from django.db import models
import uuid
import hashlib
from django.utils import timezone
from datetime import timedelta

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(null=True, blank=True)
    password = models.CharField(max_length=64)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.TextField()
    created = models.DateTimeField(auto_now_add=True) 
    exp = models.DateTimeField()
    expired_at = models.DateTimeField(null=True, blank=True)  


    def __str__(self):
        return f"{self.user.username} token"

class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.token[:8]}"
    
def _hash_otp(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


class OTP(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, db_index=True)
    otp_hash = models.CharField(max_length=128)
    otp_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_requested_ip = models.GenericIPAddressField(null=True, blank=True)

    def set_plain_otp(self, plain: str):
        self.otp_hash = _hash_otp(plain)

    def check_plain_otp(self, plain: str) -> bool:
        return _hash_otp(plain) == self.otp_hash

    def expired(self) -> bool:
        return timezone.now() > self.expires_at

    def __str__(self):
        ident = self.email or (self.user.username if self.user else "unknown")
        return f"OTP({ident}) token={self.otp_token}"


class OTPBan(models.Model):
    
    email = models.EmailField(null=True, blank=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    banned_until = models.DateTimeField()
    reason = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return self.banned_until > timezone.now()

    def __str__(self):
        return f"Ban(email={self.email} ip={self.ip} until={self.banned_until.isoformat()})"  