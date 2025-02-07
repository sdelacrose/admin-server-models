from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _


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
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    sharemundo_links_id = models.CharField(max_length=100, null=True, blank=True, unique=True, db_index=True)
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
    job_title = models.CharField(max_length=500, null=True, blank=True)
    mobile_phone = models.CharField(max_length=500, null=True, blank=True)
    street_address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    post_code = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=500, null=True, blank=True)
    license_allocated = models.BooleanField(default=False)
    linkedin_profile = models.TextField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    professional_headline = models.TextField(null=True, blank=True)
    industry = models.TextField(null=True, blank=True)
    current_position = models.TextField(null=True, blank=True)
    qualifications = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    availability_from = models.TimeField(null=True, blank=True)
    availability_until = models.TimeField(null=True, blank=True)
    availability_type = models.CharField(max_length=50, null=True, blank=True)
    availability_location = models.TextField(null=True, blank=True)
    availability_hours_per_week = models.IntegerField(null=True, blank=True)
    resume = models.TextField(null=True, blank=True)
    user_image = models.TextField(null=True, blank=True)
    user_searchable = models.BooleanField(default=False)

    preferred_language = models.CharField(
        max_length=50,
        default="English",
        choices=[
            ("English", _("English")),
            ("French", _("French")),
            ("German", _("German")),
        ],
    )
    USER_TYPE_CHOICES = [
        ("freelancer", "Freelancer"),
        ("company_user", "Company User"),
    ]

    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    

    def __str__(self):
        return str(self.email)

    @property
    def is_freelancer(self):
        """
        Check if the user is a freelancer based on user_type.
        """
        return self.user_type == 'freelancer'

    @property
    def is_company_admin(self):
        return self.company and self.company.admin_user.id == self.id
    
    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name}' 
        return ''


class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelancer_profile')
    bank_name = models.CharField(max_length=255)
    iban = models.CharField(max_length=255)
    bic = models.CharField(max_length=255)
    bank_address = models.TextField()


class BlockedToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='jwt_tokens')
    is_blocked = models.BooleanField(default=False)
    token = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


class CompanyProfile(models.Model):
    sharemundo_links_id = models.CharField(max_length=100, null=True, blank=True, unique=True, db_index=True)
    company_searchable = models.BooleanField(default=False)
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
    company_profile_image = models.TextField(null=True, blank=True)
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_profile")
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    tax_number = models.CharField(max_length=255, blank=True, null=True)
    products = models.TextField(null=True, blank=True)
    services = models.TextField(null=True, blank=True)
    expertise = models.TextField(null=True, blank=True)
    basyx_server_address = models.TextField(null=True, blank=True)
    basyx_ui_endpoint_address = models.TextField(null=True, blank=True)
    basyx_environment = models.TextField(null=True, blank=True)


    def __str__(self):
        return str(self.company_name)

class BankDetail(models.Model):
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="bank_details"
    )
    company_iban = models.TextField()
    company_bank_name = models.TextField(null=True, blank=True)
    company_bic = models.TextField(null=True, blank=True)
    company_bank_address = models.TextField(null=True, blank=True)
    company_postcode = models.TextField(null=True, blank=True)  # New field
    company_town = models.TextField(null=True, blank=True)  # New field

    def __str__(self):
        return f"{self.company.company_name} - {self.company_bank_name or 'Bank'}"


class Connection(models.Model):
    ENTITY_TYPE_CHOICES = (
        ('freelancer', 'Freelancer'),
        ('company', 'Company'),
        ('user', 'User'),
    )

    initiator_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    initiator_id = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    target_id = models.CharField(max_length=100)
    status = models.CharField(
        max_length=50,
        choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')),
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('initiator_type', 'initiator_id', 'target_type', 'target_id')


class ConnectionUser(models.Model):
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name='requested_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connection_requests')
    status = models.CharField(
        max_length=50,
        choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')),
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('connection', 'user')


class GlobalConfig(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="global_config",
        help_text="The user this configuration belongs to."
    )
    company_profile = models.OneToOneField(
        CompanyProfile, on_delete=models.CASCADE, related_name='global_config', default=None, null=True
    )
    contact_type = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    team_members_roles = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    area_of_expertise = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    funding_strategy = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    status_options = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    reminder_settings = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    invoice_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    general_tasks = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    expense_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    project_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    priority_levels = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    project_priority_levels = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )

class CompanyConfig(models.Model):
    company_profile = models.OneToOneField(
        CompanyProfile, 
        on_delete=models.CASCADE, 
        related_name='company_config',
        null=True,
        blank=True
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="freelancer_config",
        help_text="The freelancer this configuration belongs to."
    )
    contact_type = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    team_members_roles = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    area_of_expertise = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    funding_strategy = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    status_options = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    reminder_settings = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    invoice_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    general_tasks = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    expense_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    project_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    priority_levels = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    project_priority_levels = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
