from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers


class UserViewSet(ModelViewSet):
    """API Views related with user objects."""
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer


class ConditionViewSet(ModelViewSet):
    """API Views related with long term conditions."""
    queryset = models.Condition.objects.all()
    serializer_class = serializers.ConditionSerializer


class AilmentViewSet(ModelViewSet):
    """API Views related to short term ailments."""
    queryset = models.Ailment.objects.all()
    serializer_class = serializers.AilmentSerializer


class FoodViewSet(ModelViewSet):
    """API Views related with food objects."""
    queryset = models.Food.objects.all()
    serializer_class = serializers.FoodSerializer


class MealViewSet(ModelViewSet):
    """API Views related with meal objects."""
    queryset = models.Meal.objects.all()
    serializer_class = serializers.MealSerializer

    def get_queryset(self):
        """Gets the queryset for the views.

        Returns:
            Queryset of all meals filtered to the current user.
        """
        return self.queryset.filter(log__user=self.request.user)


class LogViewSet(ModelViewSet):
    """API Views related with daily logs."""
    queryset = models.Log.objects.all()
    serializer_class = serializers.LogSerializer

    def get_queryset(self):
        """Gets the queryset for the views.

        Returns:
            Queryset of all logs filtered to the current user.
        """
        return self.queryset.filter(user=self.request.user)

    @action(['GET', 'POST'], True, url_name='meal-list')
    def meals(self, request):
        """View that lists and adds meals for a log.

        POST requests will add a meal, and GET requests will list the
        meals for that log.

        Args:
            request: Request from the user.

        Returns:
            List of meals or the created meal.
        """
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







