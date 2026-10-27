from django.contrib.auth.models import BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from model_utils import FieldTracker

from .constants import GC_SKILLS, SHAREMUNDO_SOLUTION_TYPES
from .display_feature_registry import (
    DISPLAY_FEATURE_REGISTRY_VERSION,
    SolutionId,
    normalize_solution_id,
)
from .display_feature_resolver import (
    DisplayFeatureOverrideError,
    normalize_display_overrides,
)


def default_skills():
    return list(GC_SKILLS)


def default_working_days():
    """ISO weekday numbers (1=Monday..7=Sunday) that count as working days for this
    organization/country. Monday-Friday by default. Configuration only in this lot --
    not yet consulted by calculate_leave_days (balance calculation is a later lot)."""
    return [1, 2, 3, 4, 5]


def default_leave_type_organization_defaults():
    """Admin-configurable baseline for company-scope "complementary" leave types (no
    specific Admin template to inherit from) -- read live by LeaveType.effective_value,
    never copied into individual rows. Same values the 0132 backfill migration used, so
    a complementary type and a freshly-backfilled one behave identically until an Admin
    actually edits this GlobalConfig field."""
    from datetime import date

    today = date.today()
    return {
        "is_active": True,
        "deduction_mode": "working_days",
        "cycle_start_date": date(today.year, 1, 1).isoformat(),
        "cycle_end_date": date(today.year, 12, 31).isoformat(),
        "allow_half_day": False,
        "requires_supporting_document": False,
        "consumes_balance": True,
    }

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
    is_permanently_deleted = models.BooleanField(default=False) 
    permanently_deleted_at = models.DateTimeField(null=True, blank=True) 
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
    main_area_of_expertise = models.CharField(max_length=255, null=True, blank=True)
    sub_area_of_expertise = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
    )
    availability_from = models.DateField(null=True, blank=True)
    availability_until = models.DateField(null=True, blank=True)
    availability_type = models.CharField(max_length=50, null=True, blank=True)
    availability_location = models.TextField(null=True, blank=True)
    availability_hours_per_week = models.IntegerField(null=True, blank=True)
    open_to_new_challenges = models.BooleanField(default=False)
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
    spoken_languages = ArrayField(
        base_field=models.CharField(max_length=100),
        default=list,
        blank=True,
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

    def save(self, *args, **kwargs):
        if self.is_deleted and not self.deleted_at:
            self.deleted_at = timezone.now()

        super().save(*args, **kwargs)

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
    iban = models.CharField(max_length=255, null=True, blank=True)
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
    company_iban = models.TextField(null=True, blank=True)
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
    main_area_of_expertise = models.CharField(max_length=255, null=True, blank=True)
    sub_area_of_expertise = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
    )
    basyx_server_address = models.TextField(null=True, blank=True)
    basyx_ui_endpoint_address = models.TextField(null=True, blank=True)
    basyx_environment = models.TextField(null=True, blank=True)
    nace_code_one = models.TextField(null=True, blank=True)
    nace_code_two = models.TextField(null=True, blank=True)
    nace_code_three = models.TextField(null=True, blank=True)
    is_freetrial_availed = models.BooleanField(default=False)
    currency = models.CharField(max_length=100, blank=True, null=True, default="€")
    # Short code used in permanent Document references (COMPANY_CODE-DISCIPLINE_CODE-...):
    # proposed from the company name at first use, editable until the company's first
    # permanent company-level Document reference exists (checked in the `backend` repository,
    # where Document lives), then locked. Mirrors Project.project_code.
    company_code = models.CharField(max_length=10, blank=True, default="")

    tracker = FieldTracker()

    def __str__(self):
        return str(self.company_name)

    def save(self, *args, **kwargs):
        if not self.company_code:
            # Proposed once; nothing here re-derives or overwrites an existing code.
            from models.company_codes import propose_unique_company_code

            self.company_code = propose_unique_company_code(self)
        super().save(*args, **kwargs)


class SolutionDisplayConfiguration(models.Model):
    SOLUTION_CHOICES = (
        (SolutionId.ENERGY_CONSULTANT.value, "Energy Consultant Solution"),
        (SolutionId.ENTERPRISE.value, "Enterprise Solution"),
        (SolutionId.CORE.value, "Core Solution"),
    )

    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="solution_display_configurations",
    )
    solution = models.CharField(max_length=64, choices=SOLUTION_CHOICES)
    registry_version = models.PositiveIntegerField(
        default=DISPLAY_FEATURE_REGISTRY_VERSION
    )
    overrides = models.JSONField(default=dict, blank=True)
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_solution_display_configurations",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company_id", "solution"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "solution"],
                name="unique_company_solution_display_config",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        try:
            self.solution = normalize_solution_id(self.solution).value
        except ValueError as exc:
            errors["solution"] = str(exc)

        if self.registry_version < 1:
            errors["registry_version"] = "Registry version must be positive."

        if "solution" not in errors:
            try:
                self.overrides = normalize_display_overrides(
                    self.solution,
                    self.overrides,
                )
            except DisplayFeatureOverrideError as exc:
                errors["overrides"] = str(exc)

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.company} - {self.get_solution_display()}"

class BankDetail(models.Model):
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="bank_details"
    )
    company_iban = models.TextField(null=True, blank=True)
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


class StaffContractType(models.TextChoices):
    PERMANENT = "permanent", "Permanent"
    TEMPORARY = "temporary", "Temporary"


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

    # LOT RH10: no reliable contractual start/end date existed anywhere in this model
    # before this lot (confirmed: no hire/departure date field, no prior lot defining
    # one). Added as explicit, RH-configurable, nullable fields rather than inferring
    # a hire date from User.date_joined (an account-creation timestamp, not a
    # contractual date). A missing contract_start_date blocks monthly-accrual
    # processing for that employee with an explicit diagnostic -- it is never guessed.
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)

    # AI-1685: explicit temporary/permanent status -- null for existing staff
    # with no information recorded yet ("a renseigner"), NEVER inferred from
    # contract_end_date being absent (a permanent contract and an
    # unrecorded/unknown status look identical from contract_end_date alone).
    # Validated and audited at the API layer (serializers.staff), not here --
    # this field itself stays a plain, unhistorized column, same precedent as
    # contract_start_date/contract_end_date above (see
    # human_resource_management.models.staff.StaffContractAuditLog for the
    # append-only audit trail of changes to this field and to
    # contract_end_date).
    contract_type = models.CharField(
        max_length=16, choices=StaffContractType.choices, null=True, blank=True,
    )

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


class PublicHolidaySource(models.TextChoices):
    MANUAL = "manual", "Manual"
    IMPORTED = "imported", "Imported"


class GlobalPublicHoliday(models.Model):
    company_profile = models.ForeignKey(
        CompanyProfile,
        related_name="global_public_holidays",
        on_delete=models.CASCADE,
    )
    date = models.DateField()
    name = models.CharField(max_length=255)
    source = models.CharField(
        max_length=20,
        choices=PublicHolidaySource.choices,
        default=PublicHolidaySource.MANUAL,
    )
    country_code = models.CharField(max_length=10, null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name="created_global_public_holidays",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracker = FieldTracker()

    class Meta:
        ordering = ["date", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["company_profile", "date"],
                name="unique_global_public_holiday_per_company_date",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company_profile", "date"],
                name="glob_pub_hol_comp_dt_idx",
            ),
            models.Index(
                fields=["source"],
                name="glob_pub_hol_src_idx",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.date})"


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
    international_standard = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    major_project_model = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    commercial_model = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    supporting_agreement = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    team_members_roles = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    company_roles = ArrayField(
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
    document_internal_review_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_external_review_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    transmittal_category = ArrayField(
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

    leave_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    working_days = ArrayField(
        models.PositiveSmallIntegerField(),
        blank=True,
        default=default_working_days,
        help_text="ISO weekday numbers (1=Monday..7=Sunday) treated as working days "
        "for this organization/country.",
    )
    leave_type_organization_defaults = models.JSONField(
        default=default_leave_type_organization_defaults,
        blank=True,
        help_text="Admin-configurable baseline for company-scope leave types that have "
        "no specific Admin template to inherit from.",
    )
    opportunity_sales_phase = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    offer_validity_periods = ArrayField(
        models.CharField(max_length=32),
        blank=True,
        default=list,
    )
    project_service_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    labels = ArrayField(
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
    nested_configurations = models.JSONField(default=dict, blank=True)
    # Document Control settings (reference, revision, workflow); empty = canonical defaults.
    document_control_configuration = models.JSONField(default=dict, blank=True)
    configuration_visibility = models.JSONField(default=dict, blank=True)
    rooms = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    skills = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=default_skills,
    )


class ProjectConfigTemplate(models.Model):
    """Tenant-level template used to initialize and sync project configs."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="project_config_template",
    )
    company_profile = models.OneToOneField(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="project_config_template",
    )
    team_members_roles = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    funding_strategy = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    status_options = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    demand_status_options = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    requirement_status_options = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    bom_status_options = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    reminder_settings = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    document_types = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    document_status = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    document_internal_review_status = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    document_external_review_status = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    transmittal_category = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    priority_levels = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    project_service_types = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    labels = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    document_categories = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    document_disciplines = ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    nested_configurations = models.JSONField(default=dict, blank=True)
    # Document Control settings (reference, revision, workflow); empty = canonical defaults.
    document_control_configuration = models.JSONField(default=dict, blank=True)
    skills = ArrayField(
        models.CharField(max_length=255), blank=True, default=default_skills
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, company_profile__isnull=True)
                    | models.Q(user__isnull=True, company_profile__isnull=False)
                ),
                name="project_config_template_single_owner",
            )
        ]


class SupplierPaymentMethod(models.Model):
    METHOD_CARD = "card"
    METHOD_BANK_TRANSFER = "bank_transfer"
    METHOD_INVOICE = "invoice"
    METHOD_OTHER = "other"

    METHOD_TYPE_CHOICES = (
        (METHOD_CARD, "Card"),
        (METHOD_BANK_TRANSFER, "Bank transfer"),
        (METHOD_INVOICE, "Invoice"),
        (METHOD_OTHER, "Other"),
    )

    company_profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="supplier_payment_methods",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    method_type = models.CharField(
        max_length=50,
        choices=METHOD_TYPE_CHOICES,
        default=METHOD_OTHER,
    )
    display_details = models.CharField(max_length=500, blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    card_holder = models.CharField(max_length=255, blank=True, null=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    vcn_last_four = models.CharField(max_length=4, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_supplier_payment_methods",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]
        indexes = [
            models.Index(
                fields=["company_profile", "is_active"],
                name="models_supp_company_149af2_idx",
            ),
            models.Index(
                fields=["method_type"],
                name="models_supp_method__f91166_idx",
            ),
        ]

    def __str__(self):
        return self.name


class PurchasingCredential(models.Model):
    SUPPLIER_FESTO = "festo"
    SUPPLIER_WAGO = "wago"
    SUPPLIER_IFM = "ifm"
    SUPPLIER_HILSCHER = "hilscher"
    SUPPLIER_PHOENIX_CONTACT = "phoenix_contact"
    SUPPLIER_SCHNEIDER_ELECTRIC = "schneider_electric"
    SUPPLIER_OTHER = "other"

    SUPPLIER_CHOICES = (
        (SUPPLIER_FESTO, "FESTO"),
        (SUPPLIER_WAGO, "WAGO"),
        (SUPPLIER_IFM, "ifm"),
        (SUPPLIER_HILSCHER, "Hilscher"),
        (SUPPLIER_PHOENIX_CONTACT, "Phoenix Contact"),
        (SUPPLIER_SCHNEIDER_ELECTRIC, "Schneider Electric"),
        (SUPPLIER_OTHER, "Other"),
    )

    company_profile = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name="purchasing_credentials",
        null=True,
        blank=True,
    )
    supplier = models.CharField(
        max_length=100,
        choices=SUPPLIER_CHOICES,
        default=SUPPLIER_FESTO,
    )
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="created_purchasing_credentials",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["supplier", "username", "id"]
        indexes = [
            models.Index(
                fields=["company_profile", "supplier"],
                name="purch_cred_company_idx",
            ),
            models.Index(
                fields=["company_profile", "is_active"],
                name="purch_cred_active_idx",
            ),
        ]

    def __str__(self):
        return f"{self.get_supplier_display()} - {self.username}"


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
    international_standard = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    major_project_model = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    commercial_model = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    supporting_agreement = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    team_members_roles = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    company_roles = ArrayField(
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
    # LOT 3B stabilization: Correspondence Type reference data (plain labels; distinct from
    # document_types, never confused with it).
    correspondence_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_internal_review_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    document_external_review_status = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    transmittal_category = ArrayField(
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
    offer_validity_periods = ArrayField(
        models.CharField(max_length=32),
        blank=True,
        default=list,
    )
    project_service_types = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    labels = ArrayField(
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
    nested_configurations = models.JSONField(default=dict, blank=True)
    # Document Control settings (reference, revision, workflow); empty = canonical defaults.
    document_control_configuration = models.JSONField(default=dict, blank=True)
    configuration_visibility = models.JSONField(default=dict, blank=True)
    salutation = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    rooms = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list,
    )
    skills = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=default_skills,
    )
    # LOT RH 9: explicit, per-company/solution opt-in into the new
    # per-employee/per-type/per-cycle leave entitlement mechanism -- false by
    # default so existing companies keep running on the historical global
    # Staff.annual_leaves_allowed balance until their RH explicitly confirms
    # a reviewed transition (see human_resource_management.services.
    # leave_entitlement_activation). `leave_entitlement_transition_leave_type`
    # records which single LeaveType the old annual_leaves_allowed number was
    # attached to at activation time -- it is never duplicated onto any other
    # type.
    leave_entitlement_mode_active = models.BooleanField(default=False)
    leave_entitlement_activated_at = models.DateTimeField(null=True, blank=True)
    leave_entitlement_transition_leave_type = models.ForeignKey(
        'LeaveType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    # LOT RH10 follow-up: explicit per-company IANA timezone name (e.g.
    # "Europe/Paris"), required before monthly-accrual's "end of local month"
    # batch processing can run for this company. No fallback to Django's
    # global TIME_ZONE and never inferred from a country field -- a company
    # with this left unset simply cannot have its monthly accrual processed
    # automatically, and the batch job says so explicitly (see
    # human_resource_management.services.leave_accrual).
    accrual_timezone = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        unique_together = ('company_profile', 'user', 'solution')


class LeaveType(models.Model):
    """A configurable leave type, scoped either to a company's Admin defaults
    (``global_config`` set) or to one of its live per-solution configs
    (``company_config`` set) -- never both, enforced by ``leave_type_single_scope``.

    Company-scope rows may ``inherits_from`` an Admin-scope row of the same company.
    Each configurable attribute is nullable: ``None`` means "inherited from
    ``inherits_from``", a concrete value means "explicit local override". Values are
    resolved on read via ``effective_value``/``effective_config``, never copied down
    into the row automatically -- so a company row stays a thin diff against its
    Admin template until someone explicitly overrides a field.
    """

    DEDUCTION_CALENDAR_DAYS = "calendar_days"
    DEDUCTION_WORKING_DAYS = "working_days"
    DEDUCTION_MODE_CHOICES = (
        (DEDUCTION_CALENDAR_DAYS, "Calendar days"),
        (DEDUCTION_WORKING_DAYS, "Working days"),
    )

    INHERITABLE_FIELDS = (
        "is_active",
        "deduction_mode",
        "cycle_start_date",
        "cycle_end_date",
        "allow_half_day",
        "requires_supporting_document",
        "consumes_balance",
    )

    global_config = models.ForeignKey(
        GlobalConfig,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="leave_type_definitions",
        help_text="Set for an Admin-scope (company default template) leave type.",
    )
    company_config = models.ForeignKey(
        CompanyConfig,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="leave_type_definitions",
        help_text="Set for a Company-scope (live, per-solution) leave type.",
    )
    inherits_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="company_overrides",
        help_text="Admin-scope LeaveType this company-scope entry is based on.",
    )

    key = models.SlugField(
        max_length=100,
        help_text="Stable identifier (matches LeaveRequest.type going forward).",
    )
    name = models.CharField(max_length=255)

    is_active = models.BooleanField(null=True, blank=True)
    deduction_mode = models.CharField(
        max_length=20, choices=DEDUCTION_MODE_CHOICES, null=True, blank=True
    )
    cycle_start_date = models.DateField(null=True, blank=True)
    cycle_end_date = models.DateField(null=True, blank=True)
    allow_half_day = models.BooleanField(null=True, blank=True)
    requires_supporting_document = models.BooleanField(null=True, blank=True)
    consumes_balance = models.BooleanField(null=True, blank=True)

    # LOT RH10: monthly accrual mode, additive to the quota mode from LOT RH9.
    # Deliberately kept OUTSIDE INHERITABLE_FIELDS/clean()'s "required for Admin-scope
    # rows" machinery: unlike the fields above, there is no sensible organization-wide
    # default rate -- None genuinely means "this type is not configured for monthly
    # accrual" (it stays quota-mode), not "inherit a baseline". Resolved via the
    # dedicated effective_accrual_rate()/effective_accrual_effective_date() helpers
    # below, which reuse the same inherits_from fallback without the mandatory-value
    # requirement. A rate change here never rewrites LeaveAccrualCredit rows already
    # created with the previous rate (see human_resource_management.services.leave_accrual).
    monthly_accrual_rate = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Monthly accrual rate for this leave type, or None if not in monthly-accrual mode.",
    )
    accrual_effective_date = models.DateField(
        null=True,
        blank=True,
        help_text="No monthly accrual credit is generated for a period before this date.",
    )

    # LOT RH11: capped carry-over + mandatory expiration, additive to both
    # quota (RH9) and monthly-accrual (RH10) modes. Deliberately kept OUTSIDE
    # INHERITABLE_FIELDS -- disabled (False/None) is a perfectly safe default,
    # no organization-wide baseline makes sense. A later change to any of
    # these three fields never revises an already-created LeaveCycleClosure/
    # LeaveCarryOver row (see human_resource_management.services.leave_carryover) --
    # those capture the values AS APPLIED at closure time.
    carry_over_enabled = models.BooleanField(
        default=False,
        help_text="Whether unused balance is carried over to the immediately following cycle.",
    )
    carry_over_cap = models.DecimalField(
        max_digits=12, decimal_places=6, null=True, blank=True,
        help_text="None = no cap. 0 = carry-over enabled but nothing is ever actually carried.",
    )
    carry_over_expiration_months = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Required, strictly positive, whenever carry_over_enabled is True.",
    )

    # LOT RH12: part-time proration of MONTHLY ACCRUAL ONLY, additive to RH10.
    # Deliberately kept OUTSIDE INHERITABLE_FIELDS -- disabled (False) is a
    # perfectly safe default, no organization-wide baseline makes sense, and
    # activation is explicit per type (never implicit org-wide inheritance).
    # Never applied a second time to quota (RH9), carry-over (RH11) or
    # request-day-counting (services.leave_balance) -- those stay untouched.
    # Changes are historized in LeaveTypeQuotiteProrationHistory (see
    # human_resource_management.services.leave_accrual.record_policy_change);
    # this field is only ever the CURRENT value, resolved historically for a
    # given month via resolve_historical_policy, same convention as
    # monthly_accrual_rate/LeaveTypeAccrualRateHistory.
    prorate_accrual_by_quotite = models.BooleanField(
        default=False,
        help_text="Whether monthly accrual is prorated by the employee's quotite (StaffQuotiteHistory).",
    )

    # LOT L04 (SST): a stable, explicit attribute -- never a free-text/key
    # search ("maladie"/"sick"/etc. could mean anything) -- marking a type as
    # managed by the dedicated SST module rather than the classic leave form.
    # Deliberately OUTSIDE INHERITABLE_FIELDS: an SST type is never a company's
    # organization-wide default/template, it is created directly as its own
    # standalone company-scope row by the SST module. Excluded from the
    # classic form's selectable catalog (views.leave_type.applicable/admin_
    # applicable, models.leave_type_sync.sync_leave_types_array) and refused
    # outright if submitted directly to the classic LeaveRequest create/update
    # endpoints (see human_resource_management.views.leave.LeaveRequestViewSet) --
    # but otherwise a perfectly ordinary LeaveType for balance/accrual/RH13
    # purposes, reused unchanged by the SST service layer.
    is_sst_managed = models.BooleanField(
        default=False,
        help_text="Managed by the SST module -- excluded from the classic leave request form.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("global_config_id", "company_config_id", "key")
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(global_config__isnull=False, company_config__isnull=True)
                    | models.Q(global_config__isnull=True, company_config__isnull=False)
                ),
                name="leave_type_single_scope",
            ),
            models.UniqueConstraint(
                fields=("global_config", "key"),
                condition=models.Q(global_config__isnull=False),
                name="unique_admin_leave_type_key",
            ),
            models.UniqueConstraint(
                fields=("company_config", "key"),
                condition=models.Q(company_config__isnull=False),
                name="unique_company_leave_type_key",
            ),
        ]

    def __str__(self):
        scope = "admin" if self.global_config_id else "company"
        return f"{self.key} ({scope})"

    def clean(self):
        errors = {}
        if self.global_config_id and self.inherits_from_id:
            # Admin-scope rows are the root of the inheritance chain: letting one
            # inherit too would make cycle-detection below meaningless (a chain could
            # then loop admin->admin->... indefinitely), and it would defeat the
            # "Admin-scope rows always carry explicit values" guarantee the rest of
            # this validation (and effective_value's fallback logic) relies on.
            errors["inherits_from"] = "An Admin-scope leave type cannot itself inherit."
        if self.inherits_from_id and self.inherits_from_id == self.id:
            errors["inherits_from"] = "A leave type cannot inherit from itself."
        if self.company_config_id and self.inherits_from_id:
            parent = self.inherits_from
            if not parent.global_config_id:
                errors["inherits_from"] = (
                    "A company-scope leave type can only inherit from an "
                    "Admin-scope leave type."
                )
            elif (
                self.company_config
                and self.company_config.company_profile_id
                and parent.global_config.company_profile_id
                != self.company_config.company_profile_id
            ):
                errors["inherits_from"] = (
                    "Cannot inherit from another company's Admin leave type."
                )
            else:
                # Defensive: structurally a cycle can't happen once Admin-scope rows
                # are barred from inheriting (above), but walk the chain anyway in
                # case that invariant is ever relaxed.
                seen = {self.id} if self.id else set()
                node = parent
                depth = 0
                while node is not None and node.inherits_from_id:
                    if node.inherits_from_id in seen or depth > 20:
                        errors["inherits_from"] = "Inheritance cycle detected."
                        break
                    seen.add(node.id)
                    node = node.inherits_from
                    depth += 1
        if self.global_config_id:
            for field_name in self.INHERITABLE_FIELDS:
                if getattr(self, field_name) is None:
                    errors[field_name] = (
                        "This field is required for an Admin-scope leave type."
                    )
        # LOT RH11: expiration is mandatory whenever carry-over is enabled --
        # a business policy choice (see services.leave_carryover module
        # docstring), not a technical necessity, but enforced here to never
        # leave a report with no resolvable due date.
        if self.carry_over_enabled:
            if not self.carry_over_expiration_months:
                errors["carry_over_expiration_months"] = (
                    "Required and must be a strictly positive number of months "
                    "whenever carry-over is enabled."
                )
            elif self.carry_over_expiration_months <= 0:
                errors["carry_over_expiration_months"] = (
                    "Must be a strictly positive number of months."
                )
        if errors:
            raise ValidationError(errors)

    # Reads the Admin-configurable organization baseline (GlobalConfig.
    # leave_type_organization_defaults) live -- never copied into this row -- so a
    # company-only "complementary" leave type (no matching Admin template) resolves to
    # a fully working effective config without being artificially linked to some
    # unrelated Admin row just to satisfy inheritance. Falls back to the same hardcoded
    # values the 0132 backfill migration used only when no GlobalConfig exists yet, or
    # it doesn't have a value for this particular field.
    def _organization_default(self, field_name):
        from datetime import date

        today = date.today()
        hardcoded_fallback = {
            "is_active": True,
            "deduction_mode": self.DEDUCTION_WORKING_DAYS,
            "cycle_start_date": date(today.year, 1, 1),
            "cycle_end_date": date(today.year, 12, 31),
            "allow_half_day": False,
            "requires_supporting_document": False,
            "consumes_balance": True,
        }

        global_config = None
        if self.company_config_id and self.company_config.company_profile_id:
            global_config = GlobalConfig.objects.filter(
                company_profile_id=self.company_config.company_profile_id
            ).first()

        if global_config is not None:
            stored = global_config.leave_type_organization_defaults or {}
            value = stored.get(field_name)
            if value is not None:
                if field_name in ("cycle_start_date", "cycle_end_date") and isinstance(
                    value, str
                ):
                    return date.fromisoformat(value)
                return value

        return hardcoded_fallback[field_name]

    def effective_value(self, field_name):
        value = getattr(self, field_name)
        if value is not None:
            return value
        if self.inherits_from_id:
            return self.inherits_from.effective_value(field_name)
        if self.company_config_id:
            return self._organization_default(field_name)
        return None

    def effective_config(self):
        return {
            field_name: self.effective_value(field_name)
            for field_name in self.INHERITABLE_FIELDS
        }

    @property
    def overridden_fields(self):
        return {
            field_name: getattr(self, field_name) is not None
            for field_name in self.INHERITABLE_FIELDS
        }

    def effective_accrual_rate(self):
        if self.monthly_accrual_rate is not None:
            return self.monthly_accrual_rate
        if self.inherits_from_id:
            return self.inherits_from.effective_accrual_rate()
        return None

    def effective_accrual_effective_date(self):
        if self.accrual_effective_date is not None:
            return self.accrual_effective_date
        if self.inherits_from_id:
            return self.inherits_from.effective_accrual_effective_date()
        return None


class LeaveSubType(models.Model):
    """A free-form sub-type under a LeaveType, independently activatable."""

    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name="sub_types"
    )
    key = models.SlugField(max_length=100)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("leave_type_id", "key")
        constraints = [
            models.UniqueConstraint(
                fields=("leave_type", "key"),
                name="unique_leave_subtype_key_per_type",
            ),
        ]

    def __str__(self):
        return f"{self.leave_type.key}:{self.key}"


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
        related_name='company_feedbacks', 
        null=True, 
        blank=True,
        help_text="Company (Ignore if freelancer provided)"
    )
    freelancer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='freelancer_feedbacks',
        null=True, 
        blank=True,
        help_text="Freelancer (Ignore if company provided)"
    )
    solution_name = models.CharField(
        max_length=255,
        help_text="Name of the solution"
    )
    user = models.ForeignKey(   
        User, 
        on_delete=models.CASCADE, 
        related_name='user_feedbacks',
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
            models.Index(fields=['freelancer']),
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
    PROJECT_TYPE_CHOICES = (
        ('action_item', 'Action Item'),
        ('project', 'Project'),
        ('documents', 'Documents'),
        ('milestone', 'Milestone'),
        ('folder', 'Folder'),
        ('invoice', 'Invoice'),
        # ExpenseCard signals use notification_type='time_expense'
        ('time_expense', 'Expense Card'),
        ('purchase_order', 'Purchase Order'),
        ('project_funding', 'Project Funding'),
        ('project_phase', 'Project Phase'),
        ('object_assessment', 'Object Assessment'),
        ('project_team', 'Project Team'),
    )
    # Backward-compatible alias for older imports/migrations.
    TYPE_CHOICES = PROJECT_TYPE_CHOICES
    COMPANY_TYPE_CHOICES = (
        ('action_item', 'Action Item'),
        ('time_expense', 'Expense Card'),
        ('invoice', 'Invoice'),
        ('folder', 'Folder'),
        ('documents', 'Documents'),
        ('purchase_order', 'Purchase Order'),
        ('leave_request', 'Leave Request'),
        ('calendar_event', 'Calendar Event'),
        ('monthly_timesheet', 'Monthly Timesheet'),
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
    specific_notify_company_item_i_own = ArrayField(
        base_field=models.CharField(max_length=25, choices=COMPANY_TYPE_CHOICES),
        default=list,
        blank=True,
        null=True,
    )
    specific_notify_company_item_am_part_of = ArrayField(
        base_field=models.CharField(max_length=25, choices=COMPANY_TYPE_CHOICES),
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
        help_text="Company this role belongs to",
        null=True,
        blank=True,
    )
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text="Freelancer this role belongs to",
        null=True,
        blank=True,
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
        return f"{self.name} ({self.type} - {self.scope}) - {self.company.company_name if self.company else self.freelancer.full_name}"

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
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_freelancer_roles', null=True, blank=True)
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
        unique_together = ('user', 'role', 'company', 'freelancer')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class Notification(models.Model):
    TYPE_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )
    BACKEND_TYPE = (
        ('admin_backend', 'admin_backend'),
        ('backend', 'backend'),
    )
    user = models.ManyToManyField(User, related_name='notifications', blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    important = models.BooleanField(default=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    backend_type = models.CharField(max_length=15, choices=BACKEND_TYPE, null=True, blank=True, help_text="Type of backend that generated this notification")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    target = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.user} → {self.message[:20]}… [{self.content_type.model}:{self.object_id}]"
    

class NotificationSeen(models.Model):
    STATUS_CHOICES = (
        ('unread', 'Unread'),
        ('read',   'Read'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_recipients'
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='recipient_statuses'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('user', 'notification')

    def __str__(self):
        return f"{self.user} → {self.notification.id} [{self.status}]"



class APITestRun(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('finished', 'Finished'),
        ('failed', 'Failed'),
    ]

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='started'
    )

    def __str__(self):
        return f"Run {self.id} - {self.status}"



class APITestResult(models.Model):
    file = models.CharField(max_length=255)
    checked_at = models.DateTimeField()
    results = models.JSONField()

    api_test_run = models.ForeignKey(
        'APITestRun',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Result for {self.file} at {self.checked_at}"
