from modules.hr.models import (
    Employee,
    DepartmentMaster,
    LearningTracker,
    LinkedInTracker,
    JobOpening,
    InterviewGovernance,
    PartnerTracker,
    VendorPartnerHiring,
    InternshipStatus,
    BuddyEngagement,
    EmployeePerformance,
)
from modules.project.models import (
    ProjectGovernance,
    DeliverableTracker,
    CustomerSatisfaction,
    QATracker,
    ChangeRequest,
    ResourceUtilization,
    RAID,
)
from modules.customer_success.models import CustomerMaster
from modules.finance.models import POTracker, InvoiceTracker, BudgetTracker, RequestOrderTracker, PaymentTracker, RevenueTracker
from modules.sales.models import LeadTracker, SalesRevenueTracker, SalesPipeline
from modules.presales.models import (
    ProposalTracker, RFPTracker, POCTracker,
    PresalesBID, PresalesDemo, PresalesGovernance
)
from modules.marketing.models import EventWebinar, ContentBranding, Campaign
from modules.lnd.models import (
    ReusableAsset, CapabilityBuilding, PartnershipAlliance,
    TechCapability, InnovationAutomation, TrainingTracker
)
from modules.masters.models import SystemLookup

IMPORT_REGISTRY = {
    # ---------------- HR ----------------
    "department_master": {
        "model": DepartmentMaster,
        "foreign_keys": {},
        "date_fields": [],
    },
    "employee": {
        "model": Employee,
        "foreign_keys": {
            "department_id": {
                "lookup_model": DepartmentMaster,
                "lookup_column": "department_name",
                "csv_column": "department_name",
            },
            "manager_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "manager_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "manager_name",
            },
        },
        "date_fields": ["doj"],
    },
    "learning_tracker": {
        "model": LearningTracker,
        "foreign_keys": {
            "employee_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "employee_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "employee_name",
            }
        },
        "date_fields": ["training_date"],
    },
    "job_opening": {
        "model": JobOpening,
        "foreign_keys": {
            "department_id": {
                "lookup_model": DepartmentMaster,
                "lookup_column": "department_name",
                "csv_column": "department_name",
            },
            "hiring_manager_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "hiring_manager_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "hiring_manager_name",
            },
        },
        "date_fields": ["open_date", "target_closure_date"],
    },
    "linkedin_tracker": {
        "model": LinkedInTracker,
        "foreign_keys": {},
        "date_fields": ["linkedin_post_date", "last_updated"],
    },
    "interview_governance": {
        "model": InterviewGovernance,
        "foreign_keys": {
            "job_opening_id": {
                "lookup_model": JobOpening,
                "lookup_column": "req_id",
                "csv_column": "job_req_id",
            },
            "interviewer_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "interviewer_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "interviewer_name",
            },
        },
        "date_fields": ["interview_date"],
    },
    "vendor_partner_hiring": {
        "model": VendorPartnerHiring,
        "foreign_keys": {},
        "date_fields": ["request_date", "expected_joining_date"],
    },
    "internship_status": {
        "model": InternshipStatus,
        "foreign_keys": {
            "mentor_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "mentor_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "mentor_name",
            }
        },
        "date_fields": ["start_date"],
    },
    "buddy_engagement": {
        "model": BuddyEngagement,
        "foreign_keys": {
            "new_joiner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "new_joiner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "new_joiner_name",
            },
            "buddy_assigned_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "buddy_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "buddy_name",
            },
        },
        "date_fields": [],
    },
    "employee_performance": {
        "model": EmployeePerformance,
        "foreign_keys": {
            "employee_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "employee_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "employee_name",
            }
        },
        "date_fields": [],
    },
    "partner_tracker": {
        "model": PartnerTracker,
        "foreign_keys": {
            "account_manager_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "account_manager_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "account_manager_name",
            }
        },
        "date_fields": [
            "partnership_start_date",
            "expiry_date",
            "agreement_renewal_date",
        ],
    },

    # ---------------- Project ----------------
    "project_governance": {
        "model": ProjectGovernance,
        "foreign_keys": {
            "customer_id": {
                "lookup_model": CustomerMaster,
                "lookup_column": "customer_name",
                "csv_column": "customer_name",
                "export_lookup_column": "customer_name",
                "export_csv_column": "customer_name",
            },
            "pm_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "pm_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "pm_name",
            },
            "delivery_lead_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "delivery_lead_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "delivery_lead_name",
            },
        },
        "date_fields": ["start_date", "end_date"],
    },
    "deliverable_tracker": {
        "model": DeliverableTracker,
        "foreign_keys": {
            "project_id": {
                "lookup_model": ProjectGovernance,
                "lookup_column": "project_name",
                "csv_column": "project_name",
                "export_lookup_column": "project_name",
                "export_csv_column": "project_name",
            },
            "owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "owner_name",
            },
        },
        "date_fields": ["expected_date", "actual_date"],
    },
    "customer_satisfaction": {
        "model": CustomerSatisfaction,
        "foreign_keys": {
            "customer_id": {
                "lookup_model": CustomerMaster,
                "lookup_column": "customer_name",
                "csv_column": "customer_name",
                "export_lookup_column": "customer_name",
                "export_csv_column": "customer_name",
            },
            "project_id": {
                "lookup_model": ProjectGovernance,
                "lookup_column": "project_name",
                "csv_column": "project_name",
                "export_lookup_column": "project_name",
                "export_csv_column": "project_name",
            },
        },
        "date_fields": ["date_of_survey"],
    },
    "qa_tracker": {
        "model": QATracker,
        "foreign_keys": {
            "project_id": {
                "lookup_model": ProjectGovernance,
                "lookup_column": "project_name",
                "csv_column": "project_name",
                "export_lookup_column": "project_name",
                "export_csv_column": "project_name",
            },
            "owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "owner_name",
            },
        },
        "date_fields": ["audit_date"],
    },
    "change_request": {
        "model": ChangeRequest,
        "foreign_keys": {
            "project_id": {
                "lookup_model": ProjectGovernance,
                "lookup_column": "project_name",
                "csv_column": "project_name",
                "export_lookup_column": "project_name",
                "export_csv_column": "project_name",
            },
        },
        "date_fields": ["date_raised", "target_date"],
    },
    "resource_utilization": {
        "model": ResourceUtilization,
        "foreign_keys": {
            "employee_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "employee_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "employee_name",
            },
            "project_id": {
                "lookup_model": ProjectGovernance,
                "lookup_column": "project_name",
                "csv_column": "project_name",
                "export_lookup_column": "project_name",
                "export_csv_column": "project_name",
            },
        },
        "date_fields": ["allocation_start_date", "allocation_end_date"],
    },
    "raid": {
        "model": RAID,
        "foreign_keys": {
            "project_id": {
                "lookup_model": ProjectGovernance,
                "lookup_column": "project_name",
                "csv_column": "project_name",
                "export_lookup_column": "project_name",
                "export_csv_column": "project_name",
            },
            "owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "owner_name",
            },
        },
        "date_fields": ["date_raised", "target_resolution_date", "actual_resolution_date"],
    },

    # ---------------- Finance ----------------
    "po_tracker": {
        "model": POTracker,
        "foreign_keys": {
            "vendor_id": {
                "lookup_model": VendorPartnerHiring,
                "lookup_column": "vendor_name",
                "csv_column": "vendor_name",
                "export_lookup_column": "vendor_name",
                "export_csv_column": "vendor_name",
            },
            "department_id": {
                "lookup_model": DepartmentMaster,
                "lookup_column": "department_name",
                "csv_column": "department_name",
                "export_lookup_column": "department_name",
                "export_csv_column": "department_name",
            },
        },
        "date_fields": ["po_date", "expiry_date"],
    },
    "invoice_tracker": {
        "model": InvoiceTracker,
        "foreign_keys": {
            "vendor_id": {
                "lookup_model": VendorPartnerHiring,
                "lookup_column": "vendor_name",
                "csv_column": "vendor_name",
                "export_lookup_column": "vendor_name",
                "export_csv_column": "vendor_name",
            },
        },
        "date_fields": ["invoice_date", "due_date"],
    },
    "budget_tracker": {
        "model": BudgetTracker,
        "foreign_keys": {
            "department_id": {
                "lookup_model": DepartmentMaster,
                "lookup_column": "department_name",
                "csv_column": "department_name",
                "export_lookup_column": "department_name",
                "export_csv_column": "department_name",
            },
        },
        "date_fields": [],
    },
    "request_order_tracker": {
        "model": RequestOrderTracker,
        "foreign_keys": {
            "department_id": {
                "lookup_model": DepartmentMaster,
                "lookup_column": "department_name",
                "csv_column": "department_name",
                "export_lookup_column": "department_name",
                "export_csv_column": "department_name",
            },
        },
        "date_fields": ["delivery_date"],
    },
    "payment_tracker": {
        "model": PaymentTracker,
        "foreign_keys": {},
        "date_fields": [],
    },
    "revenue_tracker": {
        "model": RevenueTracker,
        "foreign_keys": {},
        "date_fields": [],
    },

    # ---------------- Sales ----------------
    "lead_tracker": {
        "model": LeadTracker,
        "foreign_keys": {
            "sales_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "sales_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "sales_owner_name",
            },
        },
        "date_fields": ["next_followup"],
    },
    "sales_revenue_tracker": {
        "model": SalesRevenueTracker,
        "foreign_keys": {
            "sales_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "sales_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "sales_owner_name",
            },
        },
        "date_fields": [],
    },
    "sales_pipeline": {
        "model": SalesPipeline,
        "foreign_keys": {
            "customer_id": {
                "lookup_model": CustomerMaster,
                "lookup_column": "customer_name",
                "csv_column": "customer_name",
                "export_lookup_column": "customer_name",
                "export_csv_column": "customer_name",
            },
            "opportunity_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "opportunity_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "opportunity_owner_name",
            },
            "revdau_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "revdau_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "revdau_owner_name",
            },
        },
        "date_fields": ["expected_closure_date"],
    },

    # ---------------- Presales ----------------
    "proposal_tracker": {
        "model": ProposalTracker,
        "foreign_keys": {
            "customer_id": {
                "lookup_model": CustomerMaster,
                "lookup_column": "customer_name",
                "csv_column": "customer_name",
                "export_lookup_column": "customer_name",
                "export_csv_column": "customer_name",
            },
            "approver_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "approver_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "approver_name",
            },
        },
        "date_fields": ["submission_date"],
    },
    "rfp_tracker": {
        "model": RFPTracker,
        "foreign_keys": {
            "customer_id": {
                "lookup_model": CustomerMaster,
                "lookup_column": "customer_name",
                "csv_column": "customer_name",
                "export_lookup_column": "customer_name",
                "export_csv_column": "customer_name",
            },
            "presales_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "presales_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "presales_owner_name",
            },
        },
        "date_fields": ["received_date", "submission_deadline"],
    },
    "poc_tracker": {
        "model": POCTracker,
        "foreign_keys": {
            "customer_id": {
                "lookup_model": CustomerMaster,
                "lookup_column": "customer_name",
                "csv_column": "customer_name",
                "export_lookup_column": "customer_name",
                "export_csv_column": "customer_name",
            },
        },
        "date_fields": ["start_date", "target_end_date", "actual_end_date"],
    },
    "presales_bid": {
        "model": PresalesBID,
        "foreign_keys": {
            "customer_id": {
                "lookup_model": CustomerMaster,
                "lookup_column": "customer_name",
                "csv_column": "customer_name",
                "export_lookup_column": "customer_name",
                "export_csv_column": "customer_name",
            },
            "solution_architect_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "solution_architect_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "solution_architect_name",
            },
        },
        "date_fields": ["start_date", "submission_date"],
    },
    "presales_demo": {
        "model": PresalesDemo,
        "foreign_keys": {
            "demo_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "demo_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "demo_owner_name",
            },
        },
        "date_fields": ["demo_date"],
    },
    "presales_governance": {
        "model": PresalesGovernance,
        "foreign_keys": {},
        "date_fields": ["review_date"],
    },

    # ---------------- Marketing ----------------
    "event_webinar": {
        "model": EventWebinar,
        "foreign_keys": {
            "owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "owner_name",
            },
        },
        "date_fields": ["event_date"],
    },
    "content_branding": {
        "model": ContentBranding,
        "foreign_keys": {
            "owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "owner_name",
            },
        },
        "date_fields": ["publish_date"],
    },
    "campaign": {
        "model": Campaign,
        "foreign_keys": {
            "campaign_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "campaign_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "campaign_owner_name",
            },
        },
        "date_fields": ["start_date", "end_date"],
    },

    # ---------------- L&D ----------------
    "reusable_asset": {
        "model": ReusableAsset,
        "foreign_keys": {
            "owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "owner_name",
            },
        },
        "date_fields": ["creation_date", "last_updated"],
    },
    "capability_building": {
        "model": CapabilityBuilding,
        "foreign_keys": {
            "employee_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "employee_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "employee_name",
            },
            "practice_owner_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "practice_owner_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "practice_owner_name",
            },
        },
        "date_fields": ["start_date", "target_completion_date", "actual_completion_date"],
    },
    "partnership_alliance": {
        "model": PartnershipAlliance,
        "foreign_keys": {},
        "date_fields": ["partnership_date", "renewal_date"],
    },
    "tech_capability": {
        "model": TechCapability,
        "foreign_keys": {},
        "date_fields": ["last_assessed_date"],
    },
    "innovation_automation": {
        "model": InnovationAutomation,
        "foreign_keys": {},
        "date_fields": ["start_date", "deployment_date"],
    },
    "training_tracker": {
        "model": TrainingTracker,
        "foreign_keys": {},
        "date_fields": ["training_start_date", "training_end_date"],
    },
    # ---------------- Masters ----------------
    "customer_master": {
        "model": CustomerMaster,
        "foreign_keys": {
            "account_manager_id": {
                "lookup_model": Employee,
                "lookup_column": "employee_code",
                "csv_column": "account_manager_code",
                "export_lookup_column": "employee_name",
                "export_csv_column": "account_manager_name",
            }
        },
        "date_fields": [],
    },
    "sys_lookup": {
        "model": SystemLookup,
        "foreign_keys": {},
        "date_fields": [],
    },
}
