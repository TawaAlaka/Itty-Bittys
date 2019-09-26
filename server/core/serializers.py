from rest_framework import serializers

from . import models


class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Info
        fields = ['birth_date', 'weight', 'height']


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Condition
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    info = InfoSerializer()

    class Meta:
        model = models.User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'info', 'conditions',
        ]


class AilmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ailment
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Food
        fields = '__all__'


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Meal
        fields = ['id', 'time', 'food']


class LogSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True)

    class Meta:
        model = models.Log
        fields = ['id', 'date', 'meals']
