from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Info(models.Model):
    birth_date = models.DateField()
    weight = models.PositiveIntegerField()
    height = models.PositiveIntegerField()


class Condition(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_analyst = models.BooleanField(default=False)
    conditions = models.ManyToManyField(Condition, blank=True)
    info = models.OneToOneField(
        Info, on_delete=models.SET_NULL, null=True, blank=True,
    )

    objects = UserManager()

    def __str__(self):
        return f'{self.email} ({self.full_name})'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_consumer(self):
        return self.info_id is not None

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Ailment(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Food(models.Model):
    name = models.CharField(max_length=255)
    calories = models.PositiveIntegerField()
    carbohydrates = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    fats = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.full_name}: {self.date}'


class Status(models.Model):
    log = models.ForeignKey(
        Log, on_delete=models.CASCADE, related_name='statuses',
    )
    condition = models.ForeignKey(Ailment, on_delete=models.PROTECT)
    time = models.TimeField(null=True)


class Meal(models.Model):
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name='meals')
    time = models.TimeField(null=True)
    food = models.ForeignKey(
        Food, on_delete=models.PROTECT, related_name='meals',
    )

    def __str__(self):
        return f'{self.log} - {self.time} {self.food}'
