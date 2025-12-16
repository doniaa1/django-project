from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=6)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
