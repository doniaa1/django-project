from rest_framework import serializers

class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    otp_token = serializers.UUIDField()
    otp_code = serializers.CharField()
