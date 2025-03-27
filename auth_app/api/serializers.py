from rest_framework import serializers
from auth_app.models import Profile

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from market_app.models import Offer


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        exclude = []


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=[('customer', 'Customer'), ('business', 'Business')])

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwörter stimmen nicht überein.")
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        profile_type = validated_data.pop('type')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        Profile.objects.create(user=user, type=profile_type)
        Token.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                "user_id": user.id
            }
        raise serializers.ValidationError("Ungültige Anmeldedaten")