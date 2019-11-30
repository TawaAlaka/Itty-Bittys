from django.db import transaction
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


def save_fields(instance, data):
    for key, value in data.items():
        setattr(instance, key, data.get(key, getattr(instance, key)))


class UserUpdateSerializer(serializers.ModelSerializer):
    info = InfoSerializer()
    conditions = serializers.PrimaryKeyRelatedField(
        queryset=models.Condition.objects.all(), many=True,
    )

    class Meta:
        model = models.User
        fields = ['email', 'first_name', 'last_name', 'info', 'conditions']

    def update(self, instance, validated_data):
        info = validated_data.pop('info', {})
        if info:
            save_fields(instance.info, info)
            instance.info.save()
        super().update(instance, validated_data)
        return instance


class UserSerializer(serializers.ModelSerializer):
    """Serializer for users."""
    info = InfoSerializer()
    conditions = ConditionSerializer(many=True)

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


class AilmentIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ailment
        fields = ['id']


class StatusSerializer(serializers.Serializer):
    ailment = serializers.IntegerField()

    def validate_ailment(self, value):
        try:
            ailment = models.Ailment.objects.get(id=value)
        except models.Ailment.DoesNotExist:
            raise serializers.ValidationError(
                'Ailment with the given ID does not exist.'
            )
        return ailment



class FoodSerializer(serializers.ModelSerializer):
    """Serializer for foods."""
    class Meta:
        model = models.Food
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    food = FoodSerializer()

    class Meta:
        model = models.Meal
        fields = ['id', 'log', 'time', 'food']


class LogMealSerializer(serializers.ModelSerializer):
    food = FoodSerializer()

    class Meta:
        model = models.Meal
        fields = ['id', 'time', 'food']


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Log
        fields = ['id', 'date']


class LogDetailSerializer(serializers.ModelSerializer):
    meals = LogMealSerializer(many=True)
    ailments = AilmentSerializer(many=True)
    calories = serializers.SerializerMethodField()
    carbohydrates = serializers.SerializerMethodField()
    proteins = serializers.SerializerMethodField()
    fats = serializers.SerializerMethodField()

    class Meta:
        model = models.Log
        fields = [
            'id', 'date', 'calories',
            'carbohydrates', 'proteins', 'fats',
            'meals', 'ailments',
        ]

    def get_calories(self, log: models.Log):
        calories = 0
        for meal in log.meals.all():
            calories += meal.food.calories
        return calories

    def get_carbohydrates(self, log: models.Log):
        carbohydrates = 0
        for meal in log.meals.all():
            carbohydrates += meal.food.carbohydrates
        return carbohydrates

    def get_proteins(self, log: models.Log):
        proteins = 0
        for meal in log.meals.all():
            proteins += meal.food.protein
        return proteins

    def get_fats(self, log: models.Log):
        fats = 0
        for meal in log.meals.all():
            fats += meal.food.fats
        return fats


class LogUpdateSerializer(serializers.ModelSerializer):
    ailments = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Ailment.objects.all()
    )

    class Meta:
        model = models.Log
        fields = ['ailments', 'date']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = ['message']


class TicketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = ['message', 'created_on']


class MealDetailSerializer(serializers.ModelSerializer):
    log = LogSerializer()
    food = FoodSerializer()

    class Meta:
        model = models.Meal
        fields = ['id', 'log', 'time', 'food']


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField()
    height = serializers.IntegerField()
    weight = serializers.IntegerField()
    birth_date = serializers.DateField()

    def validate_email(self, value):
        if models.User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Account with email already exists.',
            )
        return value

    def create(self, validated_data):
        with transaction.atomic():
            info = models.Info.objects.create(
                birth_date=validated_data.get('birth_date'),
                weight=validated_data.get('weight'),
                height=validated_data.get('height'),
            )
            user = models.User(
                email=validated_data.get('email'),
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                info=info,
            )
            user.set_password(validated_data['password'])
            user.save()
        return user



