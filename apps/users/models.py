# Django
from django.db import models
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.postgres.fields import ArrayField

# Models
from apps.general.models import Role

# Utils
from apps.general.choices import roles
from apps.general.utils import send_email_validation
from .choices import status_user


def upload_load(instance, filename):
    return f'photos_users/{instance.email}/{filename}'


class Address(models.Model):

    street = models.CharField(
        max_length=255, null=True, verbose_name='Street')
    num_int = models.PositiveSmallIntegerField(
        null=True, verbose_name='Number Intern')
    num_ext = models.PositiveSmallIntegerField(
        null=True, verbose_name='Number Extern')
    suburb = models.CharField(
        max_length=255, null=True, verbose_name='Suburb')
    town = models.CharField(
        max_length=255, null=True, verbose_name='Town')
    state = models.CharField(
        max_length=255, null=False, verbose_name='State')
    country = models.CharField(
        max_length=255, null=False, verbose_name='Coutry')
    zip_code = models.CharField(
        max_length=255, null=True, verbose_name='Zip Code')
    status_delete = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        db_table = 'address'
        ordering = ('id',)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            is_active=True,
            is_superuser=False,
            is_staff=False,
            status_delete=False,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            is_active=True,
            is_superuser=True,
            is_staff=True,
            role_id=1,
            **extra_fields,
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):

    about_me = models.CharField(
        max_length=200, null=True, verbose_name='About me')
    name = models.CharField(
        max_length=150, null=True, verbose_name='name',)
    paternal_surname = models.CharField(
        max_length=150, null=True, verbose_name='paternal surname',)
    mothers_maiden_name = models.CharField(
        max_length=150, null=True, verbose_name='mother maiden name',)
    birthdate = models.DateField(null=True, verbose_name='birthdate')
    email = models.EmailField(
        unique=True, max_length=100, null=False, verbose_name='email',)
    phone = models.CharField(verbose_name='phone', null=True, max_length=13)
    image = models.ImageField(upload_to=upload_load, default='default.jpg',
                              max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=2, null=True, verbose_name='Gender')
    subscribed = models.BooleanField(default=False)
    token = models.CharField(max_length=40, null=True, default=None)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    status_delete = models.BooleanField(default=False)
    role = models.ForeignKey(Role, choices=roles, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    hidden_fields = ArrayField(models.CharField(max_length=50), blank=True, default=[])
    status = models.CharField(choices=status_user, max_length=50,
                              default='Buscando trabajo', verbose_name='Status')

    USERNAME_FIELD = 'email'
    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'user'
        ordering = ('id',)

    def __str__(self):
        return f'{self.name} {self.email}'

    @staticmethod
    def email_message(subject, url, user, password, html):
        message = render_to_string(html, {
            'user': user.name if user.name else 'Usuario',
            'email': user.email,
            'password': password,
            'url': url,
            'uid': urlsafe_base64_encode(force_bytes(user.id)),
            'token': user.token,
            'app_name': settings.APP_NAME
        })
        send_email_validation(subject, [user.email], message)
        return True

    @ staticmethod
    def search_account(uidb64):
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64)).decode()
            user = User.objects.get(id=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    @ staticmethod
    def search_account_email(email):
        try:
            user = User.objects.get(email=email, status_delete=False)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user
