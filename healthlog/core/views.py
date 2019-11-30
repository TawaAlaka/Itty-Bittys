from typing import Dict
from datetime import date, timedelta

from django.contrib.auth import login
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from . import models, serializers, filters, forms
from .permissions import IsUnauthenticated


class AnalystRegistrationView(TemplateView):
    template_name = 'core/registration.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(
                resolve_url(settings.LOGIN_REDIRECT_URL),
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = forms.RegistrationForm(self.request.POST or None)
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        if context['form'].is_valid():
            user = context['form'].save()
            login(request, user)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return super(TemplateView, self).render_to_response(context)


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def _get_top_food_context(self, context: Dict, form_name: str):
        results = self.request.session.get('top_food_results', [])
        previous_data = self.request.session.get('top_food_form', {})
        if (
            not self.request.POST
            or (self.request.POST and not form_name == 'top_food')
        ):
            context['top_food_form'] = forms.TopFoodChoiceForm(previous_data)
            context['top_food_results'] = results
            return
        form = forms.TopFoodChoiceForm(self.request.POST)
        if not form.is_valid():
            context['top_food_form'] = form
            context['top_food_results'] = {}
            return
        queryset = models.Food.objects.all()
        min_age = form.cleaned_data['min_age']
        if min_age is not None:
            threshold = date.today() - timedelta(days=365 * min_age)
            queryset = queryset.filter(
                meals__log__user__info__birth_date__lte=threshold
            )
        max_age = form.cleaned_data['max_age']
        if max_age is not None:
            threshold = date.today() - timedelta(days=365 * max_age)
            queryset = queryset.filter(
                meals__log__user__info__birth_date__gte=threshold
            )
        condition = form.cleaned_data['condition']
        if condition is not None:
            queryset = queryset.filter(meals__log__user__conditions=condition)
        ailment = form.cleaned_data['ailment']
        if ailment is not None:
            queryset = queryset.filter(meals__log__ailments=ailment)
        min_date = form.cleaned_data['min_date']
        if min_date is not None:
            queryset = queryset.filter(meals__log__date__gte=min_date)
        max_date = form.cleaned_data['max_date']
        if max_date is not None:
            queryset = queryset.filter(meals__log__date__lte=max_date)
        limit = form.cleaned_data.get('limit', 10)
        queryset = queryset.values('name').annotate(
            total=Count('meals'),
        ).order_by('total')
        results = [result for result in queryset[:limit]]
        context['top_food_results'] = results
        context['top_food_form'] = form
        form_data = form.cleaned_data.copy()
        if form_data['ailment']:
            form_data['ailment'] = form_data['ailment'].pk
        if form_data['condition']:
            form_data['condition'] = form_data['condition'].pk
        if form_data['max_date']:
            form_data['max_date'] = str(form_data['max_date'])
        if form_data['min_date']:
            form_data['min_date'] = str(form_data['min_date'])
        self.request.session['top_food_results'] = results
        self.request.session['top_food_form'] = form_data
        print(context['top_food_results'])

    def _get_top_ailment_context(self, context: Dict, form_name: str):
        results = self.request.session.get('top_ailment_results', [])
        previous_data = self.request.session.get('top_ailment_form', {})
        if (
            not self.request.POST
            or (self.request.POST and not form_name == 'top_ailment')
        ):
            context['top_ailment_form'] = forms.TopTemporaryAilmentForm(
                previous_data,
            )
            context['top_ailment_results'] = results
            return
        form = forms.TopTemporaryAilmentForm(self.request.POST)
        if not form.is_valid():
            context['top_ailment_form'] = form
            context['top_ailment_results'] = {}
            return
        queryset = models.Ailment.objects.all()
        min_age = form.cleaned_data['min_age']
        if min_age is not None:
            threshold = date.today() - timedelta(days=365 * min_age)
            queryset = queryset.filter(
                logs__user__info__birth_date__lte=threshold
            )
        max_age = form.cleaned_data['max_age']
        if max_age is not None:
            threshold = date.today() - timedelta(days=365 * max_age)
            queryset = queryset.filter(
                logs__user__info__birth_date__gte=threshold
            )
        condition = form.cleaned_data['condition']
        if condition is not None:
            queryset = queryset.filter(logs__user__conditions=condition)
        food = form.cleaned_data['food']
        if food is not None:
            queryset = queryset.filter(logs__meals__food=food)
        min_date = form.cleaned_data['min_date']
        if min_date is not None:
            queryset = queryset.filter(logs__date__gte=min_date)
        max_date = form.cleaned_data['max_date']
        if max_date is not None:
            queryset = queryset.filter(logs__date__lte=max_date)
        limit = form.cleaned_data.get('limit', 10)
        queryset = queryset.values('name').annotate(
            total=Count('logs'),
        ).order_by('total')
        results = [result for result in queryset[:limit]]
        context['top_ailment_results'] = results
        context['top_ailment_form'] = form
        form_data = form.cleaned_data.copy()
        if form_data['food']:
            form_data['food'] = form_data['food'].pk
        if form_data['condition']:
            form_data['condition'] = form_data['condition'].pk
        if form_data['max_date']:
            form_data['max_date'] = str(form_data['max_date'])
        if form_data['min_date']:
            form_data['min_date'] = str(form_data['min_date'])
        self.request.session['top_ailment_results'] = results
        self.request.session['top_ailment_form'] = form_data
        print(context['top_ailment_results'])

    def _get_top_condition_context(self, context: Dict, form_name: str):
        results = self.request.session.get('top_condition_results', [])
        previous_data = self.request.session.get('top_condition_form', {})
        if (
            not self.request.POST
            or (self.request.POST and not form_name == 'top_condition')
        ):
            context['top_condition_form'] = forms.TopChronicConditionForm(
                previous_data,
            )
            context['top_condition_results'] = results
            return
        form = forms.TopChronicConditionForm(self.request.POST)
        if not form.is_valid():
            context['top_condition_form'] = form
            context['top_condition_results'] = {}
            return
        queryset = models.Condition.objects.all()
        min_age = form.cleaned_data['min_age']
        if min_age is not None:
            threshold = date.today() - timedelta(days=365 * min_age)
            queryset = queryset.filter(
                users__info__birth_date__lte=threshold
            )
        max_age = form.cleaned_data['max_age']
        if max_age is not None:
            threshold = date.today() - timedelta(days=365 * max_age)
            queryset = queryset.filter(
                users__info__birth_date__gte=threshold
            )
        ailment = form.cleaned_data['ailment']
        if ailment is not None:
            queryset = queryset.filter(users__logs__ailments=ailment)
        food = form.cleaned_data['food']
        if food is not None:
            queryset = queryset.filter(users__logs__meals__food=food)
        limit = form.cleaned_data.get('limit', 10)
        queryset = queryset.values('name').annotate(
            total=Count('users'),
        ).order_by('total')
        results = [result for result in queryset[:limit]]
        context['top_condition_results'] = results
        context['top_condition_form'] = form
        form_data = form.cleaned_data.copy()
        if form_data['food']:
            form_data['food'] = form_data['food'].pk
        if form_data['ailment']:
            form_data['ailment'] = form_data['ailment'].pk
        self.request.session['top_condition_results'] = results
        self.request.session['top_condition_form'] = form_data
        print(context['top_condition_results'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_name = (
            self.request.POST.get('form_name', '')
            if self.request.POST else ''
        )
        self._get_top_food_context(context, form_name)
        self._get_top_ailment_context(context, form_name)
        self._get_top_condition_context(context, form_name)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        return super().render_to_response(context)


class UserView(APIView):
    def get(self, request, format=None):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        serializer = serializers.UserUpdateSerializer(
            request.user, data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request, format=None):
        serializer = serializers.UserUpdateSerializer(
            request.user, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data)


class ConditionViewSet(
    GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """API Views related with long term conditions."""
    queryset = models.Condition.objects.all().order_by('name')
    serializer_class = serializers.ConditionSerializer
    filterset_class = filters.ConditionFilter


class AilmentViewSet(
    GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """API Views related to short term ailments."""
    queryset = models.Ailment.objects.all().order_by('name')
    serializer_class = serializers.AilmentSerializer


class FoodViewSet(
    GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """API Views related with food objects."""
    queryset = models.Food.objects.all().order_by('name')
    serializer_class = serializers.FoodSerializer
    filterset_class = filters.FoodFilter


class MealViewSet(ModelViewSet):
    """API Views related with meal objects."""
    queryset = models.Meal.objects.all().order_by('-log.time')
    serializer_class = serializers.MealSerializer
    filterset_class = filters.MealFilter

    def get_queryset(self):
        """Gets the queryset for the views.

        Returns:
            Queryset of all meals filtered to the current user.
        """
        return self.queryset.filter(log__user=self.request.user)


class TicketViewSet(GenericViewSet, mixins.CreateModelMixin):
    queryset = models.Ticket.objects.all().order_by('-created_on')

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = serializers.TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        serializer = serializers.TicketDetailSerializer(ticket)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


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

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        serializer = serializers.LogDetailSerializer(instance)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'update':
            return serializers.LogUpdateSerializer
        if self.action == 'retrieve':
            return serializers.LogDetailSerializer
        return self.serializer_class

    @action(
        ['GET', 'POST'], True, url_name='meal-list',
        serializer_class=serializers.LogMealSerializer,
    )
    def meals(self, request, pk=None):
        """View that lists and adds meals for a log.

        POST requests will add a meal, and GET requests will list the
        meals for that log.
        """
        log = self.get_object()
        # Add a meal if it's a POST request.
        if request.method == 'POST':
            serializer = serializers.LogMealSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['log'] = log
            meal = serializer.save()
            log.meals.add(meal)
            return Response(serializer.data)
        # List the current meals if it's a get request.
        if request.method == 'GET':
            meals = models.Meal.objects.filter(log=log)
            serializer = serializers.LogMealSerializer(meals, many=True)
            return Response(serializer.data)


class AuthView(ObtainAuthToken):
    serializer_class = serializers.TokenSerializer


class RegistrationView(APIView):
    permission_classes = [IsUnauthenticated]

    def post(self, request, format=None):
        serializer = serializers.RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key})




