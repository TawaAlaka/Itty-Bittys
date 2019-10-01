from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from . import models


class UserCreationForm(forms.ModelForm):
    """
    Admin form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password_one = forms.CharField(
        label='Password', widget=forms.PasswordInput,
    )
    password_two = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput,
    )

    class Meta:
        model = models.User
        fields = ('email', 'first_name', 'last_name', 'is_analyst')

    def clean_password_two(self):
        # Check that the two password entries match
        password_one = self.cleaned_data.get("password_one")
        password_two = self.cleaned_data.get("password_two")
        if password_one and password_two and password_one != password_two:
            raise forms.ValidationError("Passwords don't match")
        return password_two

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password_one"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Admin form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.User
        fields = (
            'email', 'password', 'first_name', 'last_name',
            'is_active', 'is_admin', 'is_analyst',
        )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


@admin.register(models.User)
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
            'fields': ('email', 'first_name', 'last_name', 'password_one', 'password_two')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.unregister(Group)
admin.site.register(models.Condition)
admin.site.register(models.Info)
admin.site.register(models.Food)
admin.site.register(models.Ailment)
admin.site.register(models.Log)
admin.site.register(models.Meal)
admin.site.register(models.Status)
