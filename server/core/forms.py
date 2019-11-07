from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import User


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
        model = User
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
        model = User
        fields = (
            'email', 'password', 'first_name', 'last_name',
            'is_active', 'is_admin', 'is_analyst',
        )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
