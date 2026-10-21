from sqlalchemy import Column, String, Float, Date, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from core.models import TimestampMixin


class POTracker(TimestampMixin, Base):
    __tablename__ = "po_trackers"
    po_number = Column(String, unique=True, index=True)
    request_order_id = Column(Integer, ForeignKey("request_order_trackers.id"), nullable=True)
    request_order_details = relationship("RequestOrderTracker", lazy="selectin")
    vendor_id = Column(Integer, ForeignKey("vendor_partner_hirings.id"), nullable=True)
    vendor_details = relationship("VendorPartnerHiring", lazy="selectin")
    po_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    delivery_date = Column(Date, nullable=True)
    amount = Column(Float, default=0)
    department_id = Column(Integer, ForeignKey("department_masters.id"), nullable=True)
    department_details = relationship("DepartmentMaster", lazy="selectin")
    approval_status = Column(String)
    po_status = Column(String, nullable=True)
    payment_status = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    finance_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    finance_owner_details = relationship("Employee", lazy="selectin")

    @property
    def vendor_name(self):
        if self.request_order_details and self.request_order_details.vendor_name:
            return self.request_order_details.vendor_name
        return self.vendor_details.vendor_name if self.vendor_details else None

    @property
    def project_name(self):
        return self.request_order_details.project_name if self.request_order_details else None

    @property
    def department_name(self):
        return self.department_details.department_name if self.department_details else None


class InvoiceTracker(TimestampMixin, Base):
    __tablename__ = "invoice_trackers"
    invoice_number = Column(String, unique=True, index=True)
    po_id = Column(Integer, ForeignKey("po_trackers.id"), nullable=True)
    po_details = relationship("POTracker", lazy="selectin")
    vendor_id = Column(Integer, ForeignKey("vendor_partner_hirings.id"), nullable=True)
    vendor_details = relationship("VendorPartnerHiring", lazy="selectin")
    invoice_date = Column(Date, nullable=True)
    invoice_amount = Column(Float, default=0)
    tax = Column(Float, default=0)
    due_date = Column(Date, nullable=True)
    payment_status = Column(String)
    remarks = Column(Text, nullable=True)
    finance_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    finance_owner_details = relationship("Employee", lazy="selectin")

    @property
    def po_number(self):
        return self.po_details.po_number if self.po_details else None

    @property
    def vendor_name(self):
        if self.po_details and self.po_details.vendor_name:
            return self.po_details.vendor_name
        return self.vendor_details.vendor_name if self.vendor_details else None


class BudgetTracker(TimestampMixin, Base):
    __tablename__ = "budget_trackers"
    project_id = Column(Integer, ForeignKey("project_governances.id"), nullable=True)
    project_details = relationship("ProjectGovernance", lazy="selectin")
    budget = Column(Float, default=0)
    consumed = Column(Float, default=0)
    remaining = Column(Float, default=0)
    forecast = Column(Float, default=0)
    variance = Column(Float, default=0)
    approval_status = Column(String, default="Pending Approval")
    remarks = Column(Text, nullable=True)
    finance_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    finance_owner_details = relationship("Employee", lazy="selectin")

    @property
    def project_name(self):
        return self.project_details.project_name if self.project_details else None


class RequestOrderTracker(TimestampMixin, Base):
    __tablename__ = "request_order_trackers"
    department_id = Column(Integer, ForeignKey("department_masters.id"), nullable=True)
    department_details = relationship("DepartmentMaster", lazy="selectin")
    project_id = Column(Integer, ForeignKey("project_governances.id"), nullable=True)
    project_details = relationship("ProjectGovernance", lazy="selectin")
    vendor_id = Column(Integer, ForeignKey("vendor_partner_hirings.id"), nullable=True)
    vendor_details = relationship("VendorPartnerHiring", lazy="selectin")
    item = Column(String, nullable=True)
    cost = Column(Float, default=0)
    approval_status = Column(String, default="Pending Approval")
    reason = Column(Text, nullable=True)
    finance_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    finance_owner_details = relationship("Employee", lazy="selectin")

    @property
    def department_name(self):
        return self.department_details.department_name if self.department_details else None

    @property
    def project_name(self):
        return self.project_details.project_name if self.project_details else None

    @property
    def vendor_name(self):
        return self.vendor_details.vendor_name if self.vendor_details else None


class PaymentTracker(TimestampMixin, Base):
    __tablename__ = "payment_trackers"
    payment_id = Column(String, unique=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice_trackers.id"), nullable=True)
    invoice_details = relationship("InvoiceTracker", lazy="selectin")
    vendor_id = Column(Integer, ForeignKey("vendor_partner_hirings.id"), nullable=True)
    vendor_details = relationship("VendorPartnerHiring", lazy="selectin")
    amount = Column(Float, default=0)
    method = Column(String, default="Bank Transfer")
    reference = Column(String, nullable=True)
    status = Column(String, default="Pending")
    remarks = Column(Text, nullable=True)
    finance_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    finance_owner_details = relationship("Employee", lazy="selectin")

    @property
    def invoice_number(self):
        return self.invoice_details.invoice_number if self.invoice_details else None

    @property
    def vendor_name(self):
        if self.invoice_details and self.invoice_details.vendor_name:
            return self.invoice_details.vendor_name
        return self.vendor_details.vendor_name if self.vendor_details else None


class RevenueTracker(TimestampMixin, Base):
    __tablename__ = "revenue_trackers"
    revenue_id = Column(String, unique=True, index=True)
    month = Column(String, nullable=True)
    sales_owner_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    sales_owner_details = relationship("Employee", foreign_keys=[sales_owner_id], lazy="selectin")
    payment_id = Column(Integer, ForeignKey("payment_trackers.id"), nullable=True)
    payment_details = relationship("PaymentTracker", foreign_keys=[payment_id], lazy="selectin")
    target_revenue = Column(Float, default=0)
    achieved_revenue = Column(Float, default=0)
    region = Column(String, nullable=True)
    status = Column(String, default="Open")
    remarks = Column(Text, nullable=True)

    @property
    def sales_owner_name(self):
        return self.sales_owner_details.employee_name if self.sales_owner_details else None

    @property
    def payment_reference(self):
        return self.payment_details.payment_id if self.payment_details else None

