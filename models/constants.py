from enum import Enum

SHAREMUNDO_SOLUTION_TYPES = (
    ('Core Solution', 'Core Solution'),
    ('Enterprise Solution', 'Enterprise Solution'),
    ('Energy Consultant Solution', 'Energy Consultant Solution')
)

GC_PROJECT_TYPES = ["Angebot", "iSFP", "Dachsanierung", "Other Project"]
GC_DOCUMENT_TYPES = ["Supplier Invoice", "Customer Invoice", "Contract", "Specification",
                     "Funding Request", "Confirmation of Receipt", "Funding Authorisation"]
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
GC_CALENDAR_EVENT_STATUS_OPTIONS = ["open", "in progress", "closed"]
GC_LEAVE_TYPES = ['Paid', 'Sick', 'Unpaid', 'Casual']
GC_OPPORTUNITY_SALES_PHASE = ["Identification", "Qualification", "Offer Preparation",
                              "Offer Approval", "Offer Negotiation", "Contracting", "Closed"]

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