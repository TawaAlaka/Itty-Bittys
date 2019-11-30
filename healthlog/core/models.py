from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    """Manager of all user objects."""
    def create_user(self, email, password=None):
        """Creates a user based on email and password.

        Args:
            email: Email of the user.
            password: Password of the user.

        Returns:
            Created user.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates a superuser based on email and password.

        Used when createsuperuser is called form the django
        management CLI.

        Args:
            email: Email of the user.
            password: Password of the user.

        Returns:
            Created user.
        """
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Info(models.Model):
    """User information.

    Attributes:
        birth_date: Date the user was born.
        weight: Weight of the user.
        height: Height of the user.
    """
    birth_date = models.DateField()
    weight = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.birth_date} {self.weight}lb {self.height}in'


class Condition(models.Model):
    """Long term condition associated with a user.

    Attributes:
        name: Name of the condition.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser):
    """User object.

    Attributes:
        email: Email of the user. Unique across users.
        first_name: First name of the user.
        last_name: Last name of the user.
        is_active: If the user is currently active. Disable this instead
            of deleting the user.
        is_admin: If the user is able to access the admin page.
        is_analyst: If the user has access to analyst information.
        conditions: Any long term conditions associated with the user.
        info: Information associated with the user. The presence of this
            determines if the user is an end user using the daily
            nutrition logs.
    """
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_analyst = models.BooleanField(default=False)
    conditions = models.ManyToManyField(
        Condition, blank=True, related_name='users',
    )
    info = models.OneToOneField(
        Info, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='user'
    )

    objects = UserManager()

    def __str__(self):
        """String display of the user object.

        Returns:
            Full name of the user
        """
        return self.full_name

    @property
    def full_name(self):
        """Full name of the user.

        Returns:
            Full name of the user.
        """
        return f'{self.first_name} {self.last_name}'

    @property
    def is_staff(self):
        """If the user is staff. Returns true of the user is admin.

        Returns:
            If the user is staff.
        """
        return self.is_admin

    @property
    def is_consumer(self):
        """If the user is a consumer. Returns true if they have user info.

        Returns:
            If the user is a consumer.
        """
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
    """Short term ailment associated with a particular day.

    Attributes:
        name: Name of the ailment.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Food(models.Model):
    """Food that a user has eaten.

    Attributes:
        name: Name of the food.
        calories: Number of calories in the food.
        carbohydrates: Grams of carbohydrates in the food.
        protein: Grams of proteins in the food.
        fats: Grams of fats in the food.
    """
    name = models.CharField(max_length=255)
    calories = models.PositiveIntegerField()
    carbohydrates = models.PositiveIntegerField()
    protein = models.PositiveIntegerField()
    fats = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Log(models.Model):
    """Daily log for the user.

    Attributes:
        user: User associated with the log.
        date: Date the log is associated with.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    ailments = models.ManyToManyField(Ailment, related_name='logs', blank=True)

    def __str__(self):
        return f'{self.user.full_name}: {self.date}'


class Meal(models.Model):
    """Correlation of a food with a daily log.

    Attributes:
        log: Daily log the food is associated with.
        time: Time the food was recorded.
        food: Food associated with the daily log.
    """
    BREAKFAST = 'BREAKFAST'
    LUNCH = 'LUNCH'
    DINNER = 'DINNER'
    SNACK = 'SNACK'
    TIME_CHOICES = (
        (BREAKFAST, 'Breakfast'),
        (LUNCH, 'Lunch'),
        (DINNER, 'Dinner'),
        (SNACK, 'Snack'),
    )

    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name='meals')
    time = models.CharField(max_length=255, choices=TIME_CHOICES)
    count = models.PositiveIntegerField(default=1)
    food = models.ForeignKey(
        Food, on_delete=models.PROTECT, related_name='meals',
    )

    def __str__(self):
        return f'{self.log} - {self.time} {self.food}'


class Ticket(models.Model):
    """Error that occurred with the mobile application.

    Attributes:
        user: User who had the issue.
        created_on: When the
    """
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='tickets',
    )
    created_on = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f'{self.created_on}: {self.user}'
