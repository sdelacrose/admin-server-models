from enum import Enum

SHAREMUNDO_SOLUTION_TYPES = (
    ('Core Solution', 'Core Solution'),
    ('Enterprise Solution', 'Enterprise Solution'),
    ('Energy Consultant Solution', 'Energy Consultant Solution')
)

ADMIN_SERVER_MODULES = [
    "connections",
    "users",
    "solutions",
    "licenses",
    "billing",
    "global_configurations",
    "company_profile",
    "roles",
]

SOLUTION_MODULES = [
    "notice_board",
    "projects",
    "action_item",
    "documents",
    "time_booking",
    "expense_booking",
    "invoice",
    "resources",
    "leave_request",
    "staff_observation",
    "staff_management",
    "contact_management",
    "opportunity_offers",
    "calendar_events",
    "company_configurations",
]

PROJECT_MODULES = [
    "project",
    "action_item",
    "documents",
    "object_assessments",
    "site_reporting",
    "funding",
    "phases_management",
    "milestone_management",
    "ecpmp_configurations",
]

GC_PROJECT_TYPES = ["Angebot", "iSFP", "Dachsanierung", "Other Project"]
GC_DOCUMENT_TYPES = ["Supplier Invoice:SIN", "Customer Invoice:CIN", "Contract:CON", "Specification:SPE",
                     "Funding Request:FUR", "Confirmation of Receipt:COR", "Funding Authorisation:FUA"] + ["Drawing:DRW", "Report:RPT", "Manual:MAN", "Procedure:PRO", "Other:OTH"]
GC_DOCUMENT_STATUSES = ["Complete", "Draft", "In review", "Sent"]
GC_PRIORITY_LEVELS = ["Low", "Medium", "High"]
GC_PROJECT_PRIORITY_LEVELS = ["Very Low","Low", "Medium", "High", "Very High"]

GC_EXPENSE_TYPES = ["milage", "parking", "train fare", "printing", "other"]
GC_REMINDER_SETTINGS = ["none", "1 day", "2 days", "1 week", "2 weeks"]
GC_INVOICE_STATUS = ["open", "due", "overdue", "paid", "not paid"]
GC_GENERAL_TASKS = ["office", "general", "acquisition", "IT"]
GC_STATUS_OPTIONS = ["open:#FF0000", "in progress:#FFFF00", "closed:#5CE75C"]
GC_CONTRACT_TYPES = ["Fixed Price", "Time and Material", "Other"]
GC_TEAM_MEMBERS_ROLES = ["architect", "structural engineer", "contractor", "project manager"]
GC_AREA_OF_EXPERTISE = ["HVAC services company", "carpenter", "energy consultancy"]
GC_FUNDING_STRATEGY = [
                "GEG Energy efficient Building 40", "GEG Energy efficient Building 40 EE",
                "GEG Energy efficient Building 55", "GEG Energy efficient Building 55 EE",
                "GEG Energy efficient Building 70", "GEG Energy efficient Building 70 EE",
                "GEG Energy efficient Building 85", "GEG Energy efficient Building 85 EE",
                "BEG single" ,"BEG EinzelmaBnahme + iSFP", "iSPF"
            ]
GC_LEAVE_TYPES = ['Paid', 'Sick', 'Unpaid', 'Casual']
GC_OPPORTUNITY_SALES_PHASE = ["Identification", "Qualification", "Offer Preparation",
                              "Offer Approval", "Offer Negotiation", "Contracting", "Closed"]
GC_PURCHASE_ORDER_STATUS = ["Draft", "Under Approval", "Approved", "Issued", "Closed", "Cancelled"]
GC_PROJECT_SERVICE_TYPES = []

# Document Numbering System Constants
GC_DOCUMENT_CATEGORIES = ["General:GEN", "Design:DES", "Technical:TEC",  "Manual:MAN", "Procedure:PRO", "Other:OTH"]
GC_DOCUMENT_DISCIPLINES = ["Electrical:EL", "Mechanical:ME", "Hydraulic:HY", "Architectural:AR", "Structural:ST", "Plumbing:PL", "HVAC:HV", "Other:OTH"]

# Core Solution Constants
CORE_STATUS_OPTIONS = ["open:#FF0000", "in progress:#FFFF00", "closed:#5CE75C"]
CORE_AREA_OF_EXPERTISE = ["Software Development", "Project Management", "Business Analysis"]
CORE_CONTRACT_TYPES = ["Fixed Price", "Time and Material", "Other"]
CORE_REMINDER_SETTINGS = ["none", "1 day", "2 days", "1 week", "2 weeks"]
CORE_INVOICE_STATUS = ["open", "due", "overdue", "paid", "not paid"]
CORE_GENERAL_TASKS = ["office", "general", "acquisition", "IT"]
CORE_EXPENSE_TYPES = ["milage", "parking", "train fare", "printing", "other"]
CORE_DOCUMENT_TYPES = ["Supplier Invoice", "Customer Invoice", "Contract", "Specification"]
CORE_DOCUMENT_STATUSES = ["Complete", "Draft", "In review", "Sent"]


# Enterprise Solution Constants
ENTERPRISE_STATUS_OPTIONS = ["open:#FF0000", "in progress:#FFFF00", "closed:#5CE75C"]
ENTERPRISE_AREA_OF_EXPERTISE = ["Enterprise Architecture", "Solution Architecture", "DevOps"]
ENTERPRISE_CONTRACT_TYPES = ["Fixed Price", "Time and Material", "Other"]
ENTERPRISE_TEAM_MEMBERS_ROLES = ["architect", "developer", "project manager", "business analyst"]
ENTERPRISE_REMINDER_SETTINGS = ["none", "1 day", "2 days", "1 week", "2 weeks"]
ENTERPRISE_INVOICE_STATUS = ["open", "due", "overdue", "paid", "not paid"]
ENTERPRISE_GENERAL_TASKS = ["office", "general", "acquisition", "IT"]
ENTERPRISE_EXPENSE_TYPES = ["milage", "parking", "train fare", "printing", "other"]
ENTERPRISE_PROJECT_TYPES = ["Implementation", "Migration", "Integration", "Other"]
ENTERPRISE_DOCUMENT_TYPES = ["Supplier Invoice", "Customer Invoice", "Contract", "Specification"]
ENTERPRISE_DOCUMENT_STATUSES = ["Complete", "Draft", "In review", "Sent"]

class FeedbackStatusType(Enum):
    OPEN = "open"
    INCIDENT_CREATED = "incident_created"
    IMPROVEMENT_CREATED = "improvement_created"
    NO_ACTION_REQUESTED = "no_action_requested"
    CLOSED = "closed"
    ARCHIVED = "archived"