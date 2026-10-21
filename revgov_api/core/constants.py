# core/constants.py
"""
Central place for all immutable / hard-coded values.
"""

PROJECT_NAME: str = "EGT Portal API"
VERSION: str = "1.0.0"
API_V1_STR: str = "/api/v1"

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
TOKEN_TYPE: str = "bearer"
TOKEN_TYPE_ACCESS: str = "access"
TOKEN_TYPE_REFRESH: str = "refresh"
AUTH_HEADER: str = "WWW-Authenticate"

ROLE_SUPER_ADMIN: str = "Super Admin"
ROLE_CEO: str = "CEO"
ROLE_HR_MANAGER: str = "HR Manager"
ROLE_RECRUITER: str = "Recruiter"
ROLE_FINANCE_MANAGER: str = "Finance Manager"
ROLE_PROJECT_MANAGER: str = "Project Manager"
ROLE_EMPLOYEE: str = "Employee"
ROLE_SALES_MANAGER: str = "Sales Manager"
ROLE_PRESALES_MANAGER: str = "Presales Manager"
ROLE_MARKETING_MANAGER: str = "Marketing Manager"
ROLE_L_AND_D_MANAGER: str = "L&D Manager"
ROLE_LND_MANAGER: str = ROLE_L_AND_D_MANAGER  # alias used in routes
ROLE_CUSTOMER_SUCCESS_MANAGER: str = "Customer Success Manager"
ROLE_CS_MANAGER: str = ROLE_CUSTOMER_SUCCESS_MANAGER  # alias used in routes

STATUS_ACTIVE: str = "active"
STATUS_INACTIVE: str = "inactive"
STATUS_SUSPENDED: str = "suspended"
STATUS_PENDING: str = "pending"

DEFAULT_PAGE: int = 1
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

AUTH_PREFIX: str = "/auth"
HR_PREFIX: str = "/hr"
FINANCE_PREFIX: str = "/finance"
SALES_PREFIX: str = "/sales"
PRESALES_PREFIX: str = "/presales"
MARKETING_PREFIX: str = "/marketing"
PROJECT_GOV_PREFIX: str = "/project-governance"
LEARNING_DEV_PREFIX: str = "/learning-development"
CUSTOMER_SUCCESS_PREFIX: str = "/customer-success"

ERR_INVALID_CREDENTIALS: str = "Invalid email or password"
ERR_CREDENTIALS_VALIDATE: str = "Could not validate credentials"
ERR_USER_NOT_FOUND: str = "User not found"
ERR_USER_ALREADY_EXISTS: str = "User with this email already exists"
ERR_INACTIVE_USER: str = "Inactive user"
ERR_PERMISSION_DENIED: str = "You do not have permission to perform this action"
ERR_TOKEN_EXPIRED: str = "Token has expired"
ERR_INVALID_TOKEN: str = "Invalid token"
ERR_OLD_PASSWORD_WRONG: str = "Old password is incorrect"
ERR_PASSWORD_SAME_AS_OLD: str = "New password cannot be same as old password"
ERR_PASSWORD_MISMATCH: str = "New password and confirm password do not match"
ERR_PASSWORD_WEAK: str = (
    "Password must be at least 8 characters with 1 uppercase, "
    "1 lowercase, 1 number, and 1 special character (@$!%*?&#)"
)

ERR_NOT_FOUND: str = "Resource not found"
ERR_ALREADY_EXISTS: str = "Resource already exists"
ERR_BAD_REQUEST: str = "Bad request"
ERR_INTERNAL: str = "Internal server error"

MSG_CREATED: str = "Resource created successfully"
MSG_UPDATED: str = "Resource updated successfully"
MSG_DELETED: str = "Resource deleted successfully"
MSG_SUCCESS: str = "Operation completed successfully"

DATE_FORMAT: str = "%Y-%m-%d"
DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
DATETIME_FORMAT_DISPLAY: str = "%d %b %Y, %I:%M %p"

REGEX_EMAIL: str = r"^[\w\.\+\-]+@[\w\-]+\.[\w\.\-]+$"
REGEX_PHONE_INDIA: str = r"^[6-9]\d{9}$"
REGEX_PASSWORD: str = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"
)

PREFIX_MODULE_MAP = {
    "/employees": "Masters",
    "/learning-trackers": "Learning and Development",
    "/linkedin-trackers": "HR",
    "/job-openings": "HR",
    "/interview-governance": "HR",
    "/offer-trackers": "HR",
    "/partner-trackers": "Partner Governance",
    "/vendor-partner-hiring": "Partner Governance",
    "/internship-statuses": "HR",
    "/buddy-engagements": "HR",
    "/employee-performances": "HR",
    "/department-masters": "Masters",
    "/project-governances": "Project Governance",
    "/deliverable-trackers": "Project Governance",
    "/customer-satisfactions": "Project Governance",
    "/qa-trackers": "Project Governance",
    "/change-requests": "Project Governance",
    "/resource-utilizations": "Project Governance",
    "/raids": "Project Governance",
    "/vendor-subcontractor-governances": "Project Governance",
    "/milestone-billings": "Project Governance",
    "/project-closures": "Project Governance",
    "/qbr-trackers": "Customer Success",
    "/escalation-trackers": "Customer Success",
    "/executive-connect-trackers": "Customer Success",
    "/po-trackers": "Finance",
    "/invoice-trackers": "Finance",
    "/budget-trackers": "Finance",
    "/request-order-trackers": "Finance",
    "/payment-trackers": "Finance",
    "/revenue-trackers": "Finance",
    "/reusable-assets": "Learning and Development",
    # "/knowledge-repos": "Learning and Development",
    "/capability-buildings": "Learning and Development",
    # "/partnership-alliances": "Learning and Development",
    # "/tech-capabilities": "Learning and Development",
    "/innovation-automations": "Learning and Development",
    # "/training-trackers": "Learning and Development",
    "/event-webinars": "Marketing",
    "/content-brandings": "Marketing",
    "/campaigns": "Marketing",
    "/proposal-trackers": "Presales",
    "/rfp-trackers": "Presales",
    "/poc-trackers": "Presales",
    "/presales-bids": "Presales",
    "/presales-demos": "Presales",
    "/presales-governances": "Presales",
    "/lead-trackers": "Sales",
    "/sales-revenue-trackers": "Sales",
    "/sales-pipelines": "Sales",
    "/customer-masters": "Masters",
    "/permissions": "Administration",
    "/users": "Administration",
}

PREFIX_SUBMODULE_MAP = {
    "/linkedin-trackers": "Social Media Governance",
    "/job-openings": "Social Media Governance",
    "/interview-governance": "Social Media Governance",
    "/offer-trackers": "Social Media Governance",
    "/buddy-engagements": "Employee Governance",
    "/employee-performances": "Employee Governance",
    "/internship-statuses": "Employee Governance",
}

PREFIX_TRACKER_MAP = {
    "/employees": "Employees",
    "/learning-trackers": "Learning Trackers",
    "/linkedin-trackers": "LinkedIn Trackers",
    "/job-openings": "Job Openings",
    "/interview-governance": "Interview Governance",
    "/offer-trackers": "Offer Trackers",
    "/partner-trackers": "Partner Trackers",
    "/vendor-partner-hiring": "Vendor Partner Hiring",
    "/internship-statuses": "Internship Status",
    "/buddy-engagements": "Buddy Engagements",
    "/employee-performances": "Employee Performances",
    "/department-masters": "Department Masters",
    "/project-governances": "Project Governances",
    "/deliverable-trackers": "Deliverable Trackers",
    "/customer-satisfactions": "Customer Satisfactions",
    "/qa-trackers": "QA Trackers",
    "/change-requests": "Change Requests",
    "/resource-utilizations": "Resource Utilizations",
    "/raids": "RAID Logs",
    "/vendor-subcontractor-governances": "Vendor Subcontractor Governances",
    "/milestone-billings": "Milestone Billings",
    "/project-closures": "Project Closures",
    "/qbr-trackers": "QBR Trackers",
    "/escalation-trackers": "Escalation Trackers",
    "/revenue-trackers": "Revenue Trackers",
    "/executive-connect-trackers": "Executive Connect Trackers",
    "/po-trackers": "PO Trackers",
    "/invoice-trackers": "Invoice Trackers",
    "/budget-trackers": "Budget Trackers",
    "/reusable-assets": "Reusable Assets",
    # "/knowledge-repos": "Knowledge Repos",
    "/capability-buildings": "Capability Building",
    # "/partnership-alliances": "Partnership Alliances",
    # "/tech-capabilities": "Tech Capabilities",
    "/innovation-automations": "Innovation & Automation",
    # "/training-trackers": "Training Trackers",
    "/event-webinars": "Event Webinars",
    "/content-brandings": "Content Brandings",
    "/campaigns": "Campaigns",
    "/proposal-trackers": "Proposal Trackers",
    "/rfp-trackers": "RFP Trackers",
    "/poc-trackers": "POC Trackers",
    "/presales-bids": "Presales Bids",
    "/presales-demos": "Presales Demos",
    "/presales-governances": "Presales Governances",
    "/lead-trackers": "Lead Trackers",
    "/sales-revenue-trackers": "Sales Revenue Trackers",
    "/sales-pipelines": "Sales Pipelines",
    "/customer-masters": "Customer Masters",
    "/permissions": "Permissions",
    "/users": "Users",
}

MODULES_LIST = [
    "HR",
    "Learning and Development",
    "Customer Success",
    "Masters",
    "Project Governance",
    "Sales",
    "Presales",
    "Administration",
    "Finance",
    "Marketing",
    "Partner Governance"
]

def _get_flat_default_permissions_for_role(role_name: str) -> dict:
    """
    Returns default permissions for a given role based on module structure.
    """
    if role_name == ROLE_SUPER_ADMIN:
        return {m: "CRUD" for m in MODULES_LIST}
    elif role_name == ROLE_CEO:
        return {
            "HR": "R",
            "Partner Governance": "R",
            "Learning and Development": "R",
            "Customer Success": "CRUD",
            "Masters": "R",
            "Project Governance": "R",
            "Sales": "R",
            "Presales": "R",
            "Administration": "—",
            "Finance": "CRUD",
            "Marketing": "R"
        }
    elif role_name == ROLE_CUSTOMER_SUCCESS_MANAGER:
        return {
            "HR": "R",
            "Partner Governance": "R",
            "Learning and Development": "—",
            "Customer Success": "CRUD",
            "Masters": "CRUD",
            "Project Governance": "R",
            "Sales": "—",
            "Presales": "—",
            "Administration": "—",
            "Finance": "—",
            "Marketing": "—"
        }
    elif role_name == ROLE_PROJECT_MANAGER:
        return {
            "HR": "R",
            "Partner Governance": "R",
            "Learning and Development": "R",
            "Customer Success": "R",
            "Masters": "R",
            "Project Governance": "CRUD",
            "Sales": "R",
            "Presales": "R",
            "Administration": "—",
            "Finance": "R",
            "Marketing": "R"
        }
    elif role_name == ROLE_FINANCE_MANAGER:
        return {
            "HR": "—",
            "Partner Governance": "—",
            "Learning and Development": "—",
            "Customer Success": "R",
            "Masters": "—",
            "Project Governance": "R",
            "Sales": "—",
            "Presales": "—",
            "Administration": "—",
            "Finance": "CRUD",
            "Marketing": "—"
        }
    elif role_name == ROLE_HR_MANAGER:
        return {
            "HR": "CRUD",
            "Partner Governance": "CRUD",
            "Learning and Development": "CRUD",
            "Customer Success": "—",
            "Masters": "—",
            "Project Governance": "—",
            "Sales": "—",
            "Presales": "—",
            "Administration": "—",
            "Finance": "CU",
            "Marketing": "R"
        }
    elif role_name == ROLE_SALES_MANAGER:
        return {
            "HR": "—",
            "Partner Governance": "—",
            "Learning and Development": "—",
            "Customer Success": "R",
            "Masters": "—",
            "Project Governance": "—",
            "Sales": "CRUD",
            "Presales": "R",
            "Administration": "—",
            "Finance": "—",
            "Marketing": "R"
        }
    elif role_name == ROLE_PRESALES_MANAGER:
        return {
            "HR": "—",
            "Partner Governance": "—",
            "Learning and Development": "R",
            "Customer Success": "—",
            "Masters": "—",
            "Project Governance": "—",
            "Sales": "R",
            "Presales": "CRUD",
            "Administration": "—",
            "Finance": "—",
            "Marketing": "—"
        }
    elif role_name == ROLE_MARKETING_MANAGER:
        return {
            "HR": "R",
            "Partner Governance": "R",
            "Learning and Development": "R",
            "Customer Success": "—",
            "Masters": "—",
            "Project Governance": "—",
            "Sales": "—",
            "Presales": "—",
            "Administration": "—",
            "Finance": "—",
            "Marketing": "CRUD"
        }
    elif role_name == ROLE_EMPLOYEE:
        return {
            "HR": "—",
            "Partner Governance": "—",
            "Learning and Development": "R",
            "Customer Success": "—",
            "Masters": "—",
            "Project Governance": "—",
            "Sales": "—",
            "Presales": "—",
            "Administration": "—",
            "Finance": "—",
            "Marketing": "—"
        }
    elif role_name == ROLE_RECRUITER:
        return {
            "HR": "CRUD",
            "Partner Governance": "CRUD",
            "Learning and Development": "—",
            "Customer Success": "—",
            "Masters": "—",
            "Project Governance": "—",
            "Sales": "—",
            "Presales": "—",
            "Administration": "—",
            "Finance": "—",
            "Marketing": "—"
        }
    elif role_name == ROLE_L_AND_D_MANAGER:
        return {
            "HR": "—",
            "Partner Governance": "—",
            "Learning and Development": "CRUD",
            "Customer Success": "—",
            "Masters": "—",
            "Project Governance": "—",
            "Sales": "—",
            "Presales": "—",
            "Administration": "—",
            "Finance": "—",
            "Marketing": "—"
        }

    return {m: "—" for m in MODULES_LIST}

def get_default_permissions_for_role(role_name: str) -> dict:
    """
    Returns default permissions as a nested JSON tree based on the flat structure and maps.
    """
    flat_perms = _get_flat_default_permissions_for_role(role_name)
    
    def slugify(text: str) -> str:
        if not text:
            return ""
        return text.lower().replace(" & ", "_and_").replace(" / ", "_").replace(" ", "_")

    nested_perms = {}
    
    # 1. Initialize root modules
    for mod, perm in flat_perms.items():
        mod_slug = slugify(mod)
        nested_perms[mod_slug] = {"permission": perm, "children": {}}
        
    # 2. Build the tree
    for prefix, mod in PREFIX_MODULE_MAP.items():
        mod_slug = slugify(mod)
        submod = PREFIX_SUBMODULE_MAP.get(prefix)
        track = PREFIX_TRACKER_MAP.get(prefix)
        
        if mod_slug not in nested_perms:
            continue
            
        current = nested_perms[mod_slug]["children"]
        if submod:
            submod_slug = slugify(submod)
            if submod_slug not in current:
                current[submod_slug] = {"permission": flat_perms.get(mod, "—"), "children": {}}
            current = current[submod_slug]["children"]
            
        if track:
            track_slug = slugify(track)
            if track_slug not in current:
                # Inherit the base module's permission for the tracker as default
                current[track_slug] = {"permission": flat_perms.get(mod, "—")}

    # 3. Clean up empty children nodes recursively
    def clean_empty_children(d):
        if not isinstance(d, dict): 
            return d
        if "children" in d and not d["children"]:
            del d["children"]
        elif "children" in d:
            for k, v in list(d["children"].items()):
                clean_empty_children(v)
        return d
        
    for k, v in nested_perms.items():
        clean_empty_children(v)
        
    return nested_perms
