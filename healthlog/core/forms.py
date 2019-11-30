from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password

from . import models


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput(),
    )
    password_repeated = forms.CharField(
        label='Repeat Password', widget=forms.PasswordInput(),
    )

    class Meta:
        model = models.User
        fields = ('email', 'first_name', 'last_name')

    def clean_password_repeated(self):
        password = self.cleaned_data.get('password')
        password_repeated = self.cleaned_data.get('password_repeated')
        if password != password_repeated:
            raise forms.ValidationError("Passwords don't match.")
        return password_repeated

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_analyst = True
        if commit:
            user.save()
        return user


class TopFoodChoiceForm(forms.Form):
    min_age = forms.IntegerField(min_value=0, required=False)
    max_age = forms.IntegerField(required=False)
    condition = forms.ModelChoiceField(
        models.Condition.objects.all(), required=False,
    )
    ailment = forms.ModelChoiceField(
        models.Ailment.objects.all(), required=False,
    )
    min_date = forms.DateField(required=False)
    max_date = forms.DateField(required=False)
    limit = forms.IntegerField(min_value=0, required=False)

    def clean(self):
        min_age = self.cleaned_data.get('min_age')
        max_age = self.cleaned_data.get('max_age')
        if min_age is not None and max_age is not None and min_age > max_age:
            raise forms.ValidationError(
                'Maximum age should be greater than the minimum age.',
            )
        min_date = self.cleaned_data.get('min_date')
        max_date = self.cleaned_data.get('max_date')
        if min_date is not None and max_date is not None and min_date > max_date:
            raise forms.ValidationError(
                'Maximum date should be greater than the minimum date.'
            )


class TopTemporaryAilmentForm(forms.Form):
    min_age = forms.IntegerField(min_value=0, required=False)
    max_age = forms.IntegerField(required=False)
    condition = forms.ModelChoiceField(
        models.Condition.objects.all(), required=False,
    )
    food = forms.ModelChoiceField(
        models.Food.objects.all(), required=False,
    )
    min_date = forms.DateField(required=False)
    max_date = forms.DateField(required=False)
    limit = forms.IntegerField(min_value=0, required=False)

    def clean(self):
        min_age = self.cleaned_data.get('min_age')
        max_age = self.cleaned_data.get('max_age')
        if min_age is not None and max_age is not None and min_age > max_age:
            raise forms.ValidationError(
                'Maximum age should be greater than the minimum age.',
            )
        min_date = self.cleaned_data.get('min_date')
        max_date = self.cleaned_data.get('max_date')
        if min_date is not None and max_date is not None and min_date > max_date:
            raise forms.ValidationError(
                'Maximum date should be greater than the minimum date.'
            )


class TopChronicConditionForm(forms.Form):
    min_age = forms.IntegerField(min_value=0, required=False)
    max_age = forms.IntegerField(required=False)
    ailment = forms.ModelChoiceField(
        models.Ailment.objects.all(), required=False,
    )
    food = forms.ModelChoiceField(
        models.Food.objects.all(), required=False,
    )
    limit = forms.IntegerField(min_value=0, required=False)

    def clean(self):
        min_age = self.cleaned_data.get('min_age')
        max_age = self.cleaned_data.get('max_age')
        if min_age is not None and max_age is not None and min_age > max_age:
            raise forms.ValidationError(
                'Maximum age should be greater than the minimum age.',
            )


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
