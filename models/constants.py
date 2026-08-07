from enum import Enum

SHAREMUNDO_SOLUTION_TYPES = (
    ('Core Solution', 'Core Solution'),
    ('Enterprise Solution', 'Enterprise Solution'),
    ('Energy Consultant Solution', 'Energy Consultant Solution')
)

ADMIN_SERVER_MODULES = [
    "connections",
    "users",
    "solutions_licenses",
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
    "purchase_order",
    "resources",
    "leave_request",
    "staff_observation",
    "staff_management",
    "contact_management",
    "opportunity_offers",
    "calendar_events",
    "company_configurations",
    "available_product_parts",
    "company_assembly_catalog",
    "machines",
    "equipments",
]

PROJECT_MODULES = [
    "project",
    "action_item",
    "documents",
    "calendar_events",
    "object_assessments",
    "solution_demands",
    "requirements",
    "transports",
    "bill_of_material",
    "project_assembly_catalog",
    "site_reporting",
    "funding",
    "phases_management",
    "milestone_management",
    "ecpmp_configurations",
]

GC_PROJECT_TYPES = [
    "Engineering, Design & Studies",
    "EPC / Turnkey Project",
    "Construction & Installation",
    "Commissioning & Start-up",
    "Operations & Maintenance",
    "Industrial Improvement",
    "Digital, Data & IT Project",
    "Transformation & Change",
    "Energy & Transition Project",
    "Infrastructure Project",
    "Program / Multi-Project",
    "Compliance & Regulatory Project",
]
LEGACY_GC_PROJECT_TYPES = ["Angebot", "iSFP", "Dachsanierung", "Other Project"]
LEGACY_GC_DOCUMENT_TYPES = [
    "Supplier Invoice:SIN",
    "Customer Invoice:CIN",
    "Contract:CON",
    "Specification:SPE",
    "Funding Request:FUR",
    "Confirmation of Receipt:COR",
    "Funding Authorisation:FAU",
    "Drawing:DRW",
    "Report:RPT",
    "Manual:MAN",
    "Procedure:PRO",
    "Customer Demand:CDE",
    "Other:OTH",
    "Calendar:CAL",
    "Revision:REV",
]
GC_COMPANY_DOCUMENT_TYPES = [
    "Bonds:BND",
    "Calculation:CAL",
    "Cash Flow Statement:CFS",
    "Change/Variation:CVR",
    "Claims/extension:CLX",
    "Collateral Warranty:CWA",
    "Contractor Initiated Changes:CIC",
    "Contractual Correspondence and Notices:CCN",
    "Coordination Meetings:CME",
    "CTS:CTS",
    "Data Sheet:DSH",
    "Drawing:DRW",
    "Employer's Instructions:EIN",
    "Final Payment:FPA",
    "General:GEN",
    "Hand-over:HOV",
    "HES - PD:HES",
    "Insurance:INS",
    "Interim Payment App. / Payment Notice:IPA",
    "Letter:LTR",
    "Loss and Expense Claim:LEC",
    "MOM:MOM",
    "MSDS:MSD",
    "Programme:PRG",
    "Progress Reports:PRR",
    "Punch list:PUL",
    "Quality Control Surv.:QCS",
    "Rectification Period:RCP",
    "RFI:RFI",
    "Schedule:SCH",
    "Single Line Diagram:SLD",
    "Specification:SPE",
    "Statutory Approval or Permissions:SAP",
    "Steering Committee Meeting:SCM",
]
GC_PROJECT_DOCUMENT_TYPES = [
    "Architectural view:ARV",
    "Area classification drawing:ACD",
    "Cable schedule, pipe support and spring schedule:CSP",
    "Calculations, curves, tables:CCT",
    "Call for meeting, MoM, meeting presentation, etc.:CMM",
    "Cause and effect chart:CEC",
    "Contract:CON",
    "Contracting strategy:CST",
    "Correspondence:COR",
    "Correspondence of contract:COC",
    "D model:DMD",
    "Data sheet, according to discipline:DSD",
    "Detail drawing:DDR",
    "Diagram; engineering, functional, block, interconnection, nodal, circuit:DIA",
    "Drawing:DRW",
    "Equipment layout:EQL",
    "Estimate, budget:EBU",
    "Fire protection drawing:FPD",
    "Frame agreement:FRA",
    "General and detailed specifications:GDS",
    "General arrangement drawing (guide drawing):GAD",
    "Heat and mass balance:HMB",
    "Heat tracing drawing:HTD",
    "Internal Due Diligence (IDD):IDD",
    "Isometric drawing:ISO",
    "ITB related (bid clarification):ITB",
    "Laboratory results & reports:LAB",
    "Layout of any kind (plot plan, site plan etc.):LAY",
    "Lists of any kind, index, legend:LST",
    "Loading diagram, loading plan, structural loads:LOD",
    "Logic and sequence diagram:LSD",
    "Logistic:LOG",
    "Loop diagram:LPD",
    "Maintenance information (e.g. Maintenance manual):MIN",
    "Material receiving report:MRR",
    "Material take-off (MTO):MTO",
    "Mechanical Completion and Commissioning documents:MCC",
    "Miscellaneous (not covered by any specific document type above):MSC",
    "Offer/quotation:OFQ",
    "Operational information (e.g. Operating manual):OPI",
    "Org. chart, functional descriptions etc.:ORG",
    "Permitting and Licensing:PAL",
    "Piping and instrumentation diagram (PID):PID",
    "Process flow diagram, utility flow diagram:PFD",
    "Project control (MPR, Cost report, close-out report, etc.):PCT",
    "Project design criteria; design basis, principal decisions, PCP:PDC",
    "Project procedure, work instruction, manual:PPM",
    "Purchase order:PO",
    "Report of any kind, according to discipline:RPT",
    "Requisition:REQ",
    "Sales agreement (EAR or Project Agreement):SAG",
    "Schematics:SCH",
    "System topology, system control diagram:STD",
    "Technical descriptions:TDE",
    "Termination drawing, termination details:TDD",
    "Time schedule, planning, work plan:TSP",
    "Typical drawing, sketch:TYP",
    "Verification document:VER",
]
# Backward-compatible alias used by older callers; prefer GC_COMPANY_DOCUMENT_TYPES.
GC_DOCUMENT_TYPES = list(GC_COMPANY_DOCUMENT_TYPES)
GC_DOCUMENT_STATUSES = ["Complete", "Draft", "In review", "Sent"]
GC_PRIORITY_LEVELS = ["Low", "Medium", "High"]
GC_PROJECT_PRIORITY_LEVELS = ["Very Low","Low", "Medium", "High", "Very High"]

GC_EXPENSE_TYPES = [
    "milage", "car", "hotel", "transport", "parking", "gasoline",
    "food", "taxi", "phone", "hardware", "software", "other",
]
GC_REMINDER_SETTINGS = ["none", "1 day", "2 days", "1 week", "2 weeks"]
GC_INVOICE_STATUS = ["open", "issued", "due", "overdue", "paid", "closed"]
GC_STATUS_OPTIONS = ["open:#99dce8", "in progress:#fff3ad", "closed:#bdefe0"]
GC_CONTRACT_TYPES = ["Fixed Price", "Time and Material", "Other"]
GC_TEAM_MEMBERS_ROLES = [
    "consultant",
    "project manager",
    "customer",
    "supplier",
    "notified body",
]
GC_AREA_OF_EXPERTISE = ["HVAC services company", "carpenter", "energy consultancy"]
GC_COMPANY_ROLES = ["Company Role #1", "Company Role #2", "Company Role #3"]
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
GC_DOCUMENT_CATEGORIES = ["General:GEN", "Design:DES", "Technical:TEC", "Manual:MAN", "Procedure:PRO", "Other:OTH"]
GC_DOCUMENT_DISCIPLINES = ["Electrical:EL", "Mechanical:ME", "Hydraulic:HY", "Architectural:AR", "Structural:ST", "Plumbing:PL", "HVAC:HV", "Other:OTH"]
GC_SALUTATIONS = ["Mr", "Mrs", "Miss", "X"]
GC_ROOMS = ["ROOM 1", "ROOM 2", "ROOM 3"]
GC_SKILLS = [
    "blow",
    "push",
    "move",
    "turn",
    "lift",
    "lay down",
    "heat up",
    "transport",
    "deburr",
    "drill",
    "tighten",
    "Soldering",
]

# Core Solution Constants
CORE_STATUS_OPTIONS = ["open:#99dce8", "in progress:#fff3ad", "closed:#bdefe0"]
CORE_AREA_OF_EXPERTISE = ["Software Development", "Project Management", "Business Analysis"]
CORE_CONTRACT_TYPES = ["Fixed Price", "Time and Material", "Other"]
CORE_REMINDER_SETTINGS = ["none", "1 day", "2 days", "1 week", "2 weeks"]
CORE_INVOICE_STATUS = ["open", "issued", "due", "overdue", "paid", "closed"]
CORE_EXPENSE_TYPES = [
    "milage", "car", "hotel", "transport", "parking", "gasoline",
    "food", "taxi", "phone", "hardware", "software", "other",
]
CORE_DOCUMENT_TYPES = list(GC_COMPANY_DOCUMENT_TYPES)
CORE_DOCUMENT_STATUSES = ["Complete", "Draft", "In review", "Sent"]


# Enterprise Solution Constants
ENTERPRISE_STATUS_OPTIONS = ["open:#99dce8", "in progress:#fff3ad", "closed:#bdefe0"]
ENTERPRISE_AREA_OF_EXPERTISE = ["Enterprise Architecture", "Solution Architecture", "DevOps"]
ENTERPRISE_CONTRACT_TYPES = ["Fixed Price", "Time and Material", "Other"]
ENTERPRISE_TEAM_MEMBERS_ROLES = ["architect", "developer", "project manager", "business analyst"]
ENTERPRISE_REMINDER_SETTINGS = ["none", "1 day", "2 days", "1 week", "2 weeks"]
ENTERPRISE_INVOICE_STATUS = ["open", "issued", "due", "overdue", "paid", "closed"]
ENTERPRISE_EXPENSE_TYPES = [
    "milage", "car", "hotel", "transport", "parking", "gasoline",
    "food", "taxi", "phone", "hardware", "software", "other",
]
ENTERPRISE_PROJECT_TYPES = GC_PROJECT_TYPES
ENTERPRISE_DOCUMENT_TYPES = list(GC_COMPANY_DOCUMENT_TYPES)
ENTERPRISE_DOCUMENT_STATUSES = ["Complete", "Draft", "In review", "Sent"]

class FeedbackStatusType(Enum):
    OPEN = "open"
    INCIDENT_CREATED = "incident_created"
    IMPROVEMENT_CREATED = "improvement_created"
    NO_ACTION_REQUESTED = "no_action_requested"
    CLOSED = "closed"
    ARCHIVED = "archived"


ENTERPRISE_SOLUTION = "Enterprise Solution"
ENERGY_CONSULTANT_SOLUTION = "Energy Consultant Solution"
CORE_SOLUTION = "Core Solution"

#ADMIN SERVER LEVEL ROLES (COMPANY)
COMPANY_OWNER = 'Company Owner'
COMPANY_ADMIN_ADMIN_SERVER = 'Company Administrator – Admin Server'
COMPANY_USER_ADMIN_SERVER = 'Company Admin User'
COMPANY_USER = 'Company User – Admin Panel'
CONNECTION_MANAGER = 'Connection Manager'
ROLES_MANAGER = 'Roles Manager'

#SOLUTION LEVEL ROLES (COMPANY)

SOLUTION_COMPANY_OWNER = 'Company Owner'
SOLUTION_COMPANY_ADMINISTRATOR = 'Company Administrator'
SOLUTION_COMPANY_PROJECT_MANAGER = 'Company Project Manager'
SOLUTION_COMPANY_USER = 'Company User'
SOLUTION_HR_MANAGER = 'HR Manager'

#PROJECT LEVEL ROLES (COMPANY)
PROJECT_OWNER = 'Project Owner'
PROJECT_MANAGER = 'Project Manager'
PROJECT_USER_INTERNAL = 'Project User – Internal'
PROJECT_USER_EXTERNAL = 'Project User - External'

# FREELANCER LEVEL ROLES (FREELANCER)
FREELANCER_ADMIN_SERVER_OWNER = "FREELANCER_ADMIN_SERVER"
FREELANCER_SOLUTION_OWNER = "FREELANCER_SOLUTION"


FREELANCER_PROJECT_OWNER = 'Project Owner'
FREELANCER_PROJECT_MANAGER = 'Project Manager'
FREELANCER_PROJECT_USER_INTERNAL = 'Project User – Internal'
FREELANCER_PROJECT_USER_EXTERNAL = 'Project User - External'
