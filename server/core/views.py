from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer



class ConditionViewSet(ModelViewSet):
    queryset = models.Condition.objects.all()
    serializer_class = serializers.ConditionSerializer


class AilmentViewSet(ModelViewSet):
    queryset = models.Ailment.objects.all()
    serializer_class = serializers.AilmentSerializer


class FoodViewSet(ModelViewSet):
    queryset = models.Food.objects.all()
    serializer_class = serializers.FoodSerializer


class MealViewSet(ModelViewSet):
    queryset = models.Meal.objects.all()
    serializer_class = serializers.MealSerializer

    def get_queryset(self):
        return self.queryset.filter(log__user=self.request.user)


class LogViewSet(ModelViewSet):
    queryset = models.Log.objects.all()
    serializer_class = serializers.LogSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(['GET', 'POST'], True, url_name='meal-list')
    def meals(self, request):
        log = self.get_object()
        # Add a meal if it's a POST request.
        if request.method == 'POST':
            serializer = serializers.MealSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            meal = serializer.save()
            log.meals.add(meal)
            return Response(serializer.data)
        # List the current meals if it's a get request.
        if request.method == 'GET':
            meals = models.Meal.objects.filter(log=log)
            serializer = serializers.MealSerializer(meals, many=True)
            return Response(serializer.data)







