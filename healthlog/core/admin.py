from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models
from .forms import UserChangeForm, UserCreationForm


class CustomAdminSite(AdminSite):
    site_header = _('Health Log Administration')
    site_title = _('Health Log Administration')


class ConditionInlineAdmin(admin.TabularInline):
    model = models.User.conditions.through
    extra = 1


class AilmentInlineAdmin(admin.TabularInline):
    model = models.Log.ailments.through
    extra = 1


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_admin')
    list_filter = ('is_admin', 'is_analyst')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Details', {'fields': ('first_name', 'last_name', 'info')}),
        ('Permissions', {'fields': ('is_admin', 'is_analyst')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name',
                'password_one', 'password_two',
            ),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()
    inlines = (ConditionInlineAdmin,)


class InfoAdmin(admin.ModelAdmin):
    model = models.Info
    list_display = ('user', 'birth_date', 'weight', 'height')
    search_fields = ('user',)


class FoodAdmin(admin.ModelAdmin):
    model = models.Food
    list_display = ('name', 'calories', 'carbohydrates', 'protein', 'fats')
    search_fields = ('name',)
    ordering = ('name',)


class LogAdmin(admin.ModelAdmin):
    model = models.Log
    list_display = ('date', 'user')
    search_fields = ('user',)
    ordering = ('-date',)


class MealAdmin(admin.ModelAdmin):
    model = models.Meal
    list_display = ('log', 'time', 'food')
    search_fields = ('log', 'food',)
    list_filter = ('time',)


class TicketAdmin(admin.ModelAdmin):
    model = models.Ticket
    list_display = ('created_on', 'user')
    search_fields = ('message',)


site = CustomAdminSite()
site.register(models.User, UserAdmin)
site.register(models.Condition)
site.register(models.Info, InfoAdmin)
site.register(models.Food, FoodAdmin)
site.register(models.Ailment)
site.register(models.Log, LogAdmin)
site.register(models.Meal, MealAdmin)
site.register(models.Ticket, TicketAdmin)
