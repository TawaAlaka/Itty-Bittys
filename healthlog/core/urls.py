"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import re
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.contrib.auth import views as auth_views
from rest_framework.routers import SimpleRouter

from . import views
from . import admin

router = SimpleRouter()

# API Router information.
router.register(r'ailments', views.AilmentViewSet)
router.register(r'conditions', views.ConditionViewSet)
router.register(r'foods', views.FoodViewSet)
router.register(r'logs', views.LogViewSet)
router.register(r'meals', views.MealViewSet)

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'registration/', views.AnalystRegistrationView.as_view(),
        name='analyst-registration',
    ),
    path('admin/', admin.site.urls),  # Admin page
    path('api/auth/', views.AuthView.as_view()),  # Authentication
    path('api/registration/', views.RegistrationView.as_view()),
    path('api/users/me/', views.UserView.as_view()),
    path('api/', include(router.urls)),  # API route
] + [
    re_path(
        r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')),
        serve, {'document_root': settings.STATIC_ROOT}
    ),
]
