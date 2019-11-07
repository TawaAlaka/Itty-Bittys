from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from . import models


class TokenSerializer(serializers.Serializer):
    """Serializer for token authentication."""
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email, password=password,
            )
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class InfoSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    class Meta:
        model = models.Info
        fields = ['birth_date', 'weight', 'height']


class ConditionSerializer(serializers.ModelSerializer):
    """Serializer for long term user ailments."""
    class Meta:
        model = models.Condition
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""
    info = InfoSerializer()

    class Meta:
        model = models.User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'info', 'conditions',
        ]


class AilmentSerializer(serializers.ModelSerializer):
    """Serializer for short term ailments."""
    class Meta:
        model = models.Ailment
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    """Serializer for foods."""
    class Meta:
        model = models.Food
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    """Serializer for meals."""
    class Meta:
        model = models.Meal
        fields = ['id', 'time', 'food']


class LogSerializer(serializers.ModelSerializer):
    """
    Serializers for daily logs.

    Attributes:
        meals: meal information associated with the daily log.
    """
    meals = MealSerializer(many=True)

    class Meta:
        model = models.Log
        fields = ['id', 'date', 'meals']
