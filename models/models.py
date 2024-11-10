from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    auth0_sub = models.CharField(max_length=400, null=True, blank=True)
    company = models.ForeignKey('CompanyProfile', on_delete=models.SET_NULL, related_name='users', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.email)


class BlockedToken(models.Model):
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class CompanyProfile(models.Model):
    company_name = models.TextField(null=True, blank=True)
    company_address = models.TextField()
    company_registration_no = models.TextField(null=True, blank=True)
    post_code = models.TextField(default=0000)
    company_town = models.TextField()
    company_country = models.TextField(null=True, blank=True)
    company_tell_no = models.TextField()
    company_mob_no = models.TextField()
    company_web_address = models.TextField()
    company_email_address = models.TextField()
    company_tax_reference = models.TextField()
    company_iban = models.TextField()
    company_bank_name = models.TextField(null=True,blank=True)
    company_bic = models.TextField(null=True, blank=True)
    company_bank_address = models.TextField(null=True, blank=True)
    company_image = models.ImageField(upload_to="company_images", null=True, blank=True)
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_profile")
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    tax_number = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return str(self.company_name)
