from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from .constants import SHAREMUNDO_SOLUTION_TYPES

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
    is_freetrial_availed = models.BooleanField(default=False)

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
    currency = models.CharField(max_length=100, blank=True, null=True, default="€")



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
    nace_code_one = models.TextField(null=True, blank=True)
    nace_code_two = models.TextField(null=True, blank=True)
    nace_code_three = models.TextField(null=True, blank=True)
    is_freetrial_availed = models.BooleanField(default=False)
    currency = models.CharField(max_length=100, blank=True, null=True, default="€")


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


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff')
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='subordinates'
    )
    salary = models.FloatField()
    productivity_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    annual_leaves_allowed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=12)
    wfh_leaves_allowed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=12)
    weekly_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hourly_rate = models.FloatField(null=True, blank=True, default=75)

    def __str__(self):
        return f"{self.user.email}"


class StaffConfiguration(models.Model):
    company_profile = models.OneToOneField(CompanyProfile, on_delete=models.CASCADE, related_name="staff_configuration", null=True, blank=True)
    freelancer = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_configuration", null=True, blank=True)
    number_of_hours = models.IntegerField()
    number_of_leaves = models.IntegerField()
    number_of_wfh_leaves = models.IntegerField()
    hourly_rate = models.IntegerField()
    base_salary = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserOutlookCredentials(models.Model):
    user = models.OneToOneField(User, related_name="outlook_credentials", on_delete=models.CASCADE)
    outlook_access_token = models.TextField(null=True, blank=True)
    outlook_refresh_token = models.TextField(null=True, blank=True)
    outlook_token_expires = models.DateTimeField(null=True, blank=True)


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
    contract_type = ArrayField(
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
    calendar_event_status_options = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    leave_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    opportunity_sales_phase = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    project_service_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    purchase_order_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_categories = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_disciplines = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )

class CompanyConfig(models.Model):
    solution = models.CharField(max_length=255, choices=SHAREMUNDO_SOLUTION_TYPES, default="Energy Consultant Solution")

    company_profile = models.ForeignKey(
        CompanyProfile, 
        on_delete=models.CASCADE, 
        related_name='company_config',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="freelancer_config",
        help_text="The freelancer this configuration belongs to."
    )
    contract_type = ArrayField(
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
    calendar_event_status_options = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    leave_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    opportunity_sales_phase = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    project_service_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    purchase_order_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_categories = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_disciplines = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )

    class Meta:
        unique_together = ('company_profile', 'user', 'solution')

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('suggestion', 'Suggestion'),
        ('incident', 'Incident'),
        ('bug', 'Bug'),
        ('improvement', 'Improvement Request')
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('incident_created', 'Incident Created'),
        ('improvement_created', 'Improvement Created'),
        ('no_action', 'No Action Requested'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    # Meta Information
    company_profile = models.ForeignKey(
        CompanyProfile, 
        on_delete=models.CASCADE, 
        related_name='feedbacks', 
        null=True, 
        blank=True,
        help_text="User's Company (Ignore if freelancer)"
    )
    solution_name = models.CharField(
        max_length=255,
        help_text="Name of the solution"
    )
    user = models.ForeignKey(   
        User, 
        on_delete=models.CASCADE, 
        related_name='feedbacks',
        help_text="User who created the feedback",
        null=True,
        blank=True,
    )
    project = models.IntegerField(null=True, blank=True, help_text="Project ID (if it's regarding project)")
    project_name = models.CharField(max_length=255, null=True, blank=True, help_text="Project Name (if it's regarding project)")
    project_team_role = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Project Team Member Role (if it's regarding project)"
    )



    # Feedback Details
    feedback_type = models.CharField(
        max_length=50, 
        choices=FEEDBACK_TYPES,
        help_text="Type of feedback (Suggestion/incident/bug/improvement request)"
    )
    description = models.TextField(
        help_text="Description of the feedback"
    )
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='open',
        help_text="Status of the feedback (Open/Incident created/Improvement created/No action requested/Closed)"
    )
    answer_required = models.BooleanField(
        default=True,
        help_text="Whether an answer is required for this feedback"
    )

    # Attachments
    attachments = ArrayField(
        models.CharField(max_length=1000),
        blank=True,
        null=True,
        default=list,
    )
    
    # Admin Response
    admin_response = models.TextField(
        null=True, 
        blank=True,
        help_text="Response from Sharemundo admin"
    )
    responded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='responded_feedbacks', 
        null=True, 
        blank=True,
        help_text="Sharemundo admin who responded"
    )
    response_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date when admin responded"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the feedback was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the feedback was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['feedback_type']),
            models.Index(fields=['company_profile']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Feedback #{self.id} - {self.feedback_type}"

    def save(self, *args, **kwargs):
        # If status is changed to 'closed', ensure response_date is set
        if self.status == 'closed' and not self.response_date:
            self.response_date = timezone.now()
        super().save(*args, **kwargs)

class FeedbackResponse(models.Model):
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="The feedback this response belongs to"
    )
    response = models.TextField(
        help_text="Response from Sharemundo admin"
    )
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='feedback_responses',
        null=True,
        help_text="Sharemundo admin who responded"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the response was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the response was last updated"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "Feedback Response"
        verbose_name_plural = "Feedback Responses"
        indexes = [
            models.Index(fields=['feedback']),
            models.Index(fields=['created_at']),
            models.Index(fields=['responded_by']),
        ]

    def __str__(self):
        return f"Response to Feedback #{self.feedback.id} by {self.responded_by}"

class Preference(models.Model):
    TYPE_CHOICES = (
        ('action_item', 'Action Item'),
        ('project', 'Project'),
        ('time_expense', 'Time/Expense'),
        ('documents', 'Documents'),
        ('milestone', 'Milestone'),
        ('folder', 'Folder'),
        ('invoice', 'Invoice'),
        ('time_card', 'Time Card'),
        ('expense_card', 'Expense Card'),
        ('purchase_order', 'Purchase Order'),
        ('project_funding', 'Project Funding'),
        ('project_phase', 'Project Phase'),
        ('object_assessment', 'Object Assessment'),
        ('project_team', 'Project Team'),
        ('project_external_user', 'Project External User'),
        ('ecpmp_config', 'ECPMP Config'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference')
    notify_item_created_by_me = models.BooleanField(default=False)
    notify_item_i_own = models.BooleanField(default=False)
    notify_item_am_part = models.BooleanField(default=False)
    specific_notify_item_i_own      = ArrayField(
        base_field=models.CharField(max_length=25, choices=TYPE_CHOICES),
        default=list,
        blank=True,
        null=True,
    )
    specific_notify_item_am_part_of = ArrayField(
        base_field=models.CharField(max_length=25, choices=TYPE_CHOICES),
        default=list,
        blank=True,
        null=True,
    )
    email_check = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Permission(models.Model):
    """
    Permissions table to store all available permissions
    """
    key = models.CharField(max_length=255, unique=True, help_text="Permission key (e.g., action_item.view)")
    name = models.CharField(max_length=255, help_text="Human readable permission name")
    description = models.TextField(blank=True, null=True, help_text="Permission description")
    module = models.CharField(max_length=100, help_text="Module this permission belongs to (e.g., action_item, document)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['module', 'key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['module']),
            # Add composite indexes for common filter combinations
            models.Index(fields=['module', 'key']),
        ]

    def __str__(self):
        return f"{self.key} - {self.name}"

class Role(models.Model):
    """
    Roles table to store admin_server and solution level roles
    """
    name = models.CharField(max_length=255, help_text="Role name")
    description = models.TextField(blank=True, null=True, help_text="Role description")
    company = models.ForeignKey(
        CompanyProfile, 
        on_delete=models.CASCADE, 
        related_name='roles',
        help_text="Company this role belongs to"
    )
    type = models.CharField(
        max_length=20,
        choices=[('admin_server', 'Admin Server'), ('solution', 'Solution')],
        help_text="Type of role - admin_server or solution"
    )
    scope = models.CharField(
        max_length=20, 
        choices=[('company', 'Company'), ('project', 'Project')],
        help_text="Scope of this role"
    )
    is_default = models.BooleanField(
        default=False, 
        help_text="Whether this is a default role created by the system"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this role is active")
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='created_roles',
        null=True, 
        blank=True,
        help_text="User who created this role"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'company', 'type', 'scope')
        ordering = ['type', 'name']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['type']),
            models.Index(fields=['scope']),
            models.Index(fields=['is_default']),
            models.Index(fields=['is_active']),
            # Add composite indexes for common filter combinations
            models.Index(fields=['type', 'scope']),
            models.Index(fields=['company', 'type', 'scope']),
        ]

    def __str__(self):
        return f"{self.name} ({self.type} - {self.scope}) - {self.company.company_name}"

class RolePermission(models.Model):
    """
    Junction table to link roles with permissions
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('role', 'permission')
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['permission']),
            # Add composite indexes for role filtering
            models.Index(fields=['role', 'permission']),
        ]

    def __str__(self):
        return f"{self.role.name} - {self.permission.key}"

class UserRole(models.Model):
    """
    Junction table to assign roles to users with scope
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_company_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_company_roles')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='user_company_roles', null=True, blank=True)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='assigned_company_roles',
        null=True, 
        blank=True,
        help_text="User who assigned this role"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'role')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
