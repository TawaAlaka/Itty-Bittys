import django_filters as filters

from . import models


class FoodFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Food
        fields = ['name']


class ConditionFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Condition
        fields = ['name']


class MealFilter(filters.FilterSet):
    before = filters.DateFilter(field_name='log__date', lookup_expr='lte')
    after = filters.DateFilter(field_name='log__date', lookup_expr='gte')

    class Meta:
        model = models.Meal
        fields = []


class LogFilter(filters.FilterSet):
    before = filters.DateFilter(field_name='date', lookup_expr='lte')
    after = filters.DateFilter(field_name='date', lookup_expr='gte')

    class Meta:
        model = models.Log
        fields = []
