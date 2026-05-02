import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class PaymentEntry(Document):
    def validate(self):
        from vj_biofuel.vj_bio_fuel.accounts_utils import check_freeze_period
        check_freeze_period(self.posting_date)
        
        self.validate_details()
        self.validate_outstanding()

    def validate_details(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Payment amount must be greater than 0"))
        
        if self.reference_invoice:
            si_status = frappe.db.get_value("Sales Invoice", self.reference_invoice, "docstatus")
            if si_status != 1:
                frappe.throw(_("Reference Invoice {0} must be submitted").format(self.reference_invoice))
            
            si_customer = frappe.db.get_value("Sales Invoice", self.reference_invoice, "customer")
            if si_customer != self.customer:
                frappe.throw(_("Reference Invoice {0} belongs to customer {1}, not {2}")
                    .format(self.reference_invoice, si_customer, self.customer))

    def validate_outstanding(self):
        if self.reference_invoice:
            from vj_biofuel.vj_bio_fuel.accounts_utils import get_invoice_outstanding
            outstanding = get_invoice_outstanding(self.reference_invoice)
            
            # If it's a new payment, outstanding is current. 
            # If it's an update, we'd need more complex logic, but here we only allow creation.
            if flt(self.amount) > flt(outstanding):
                frappe.throw(_("Payment amount {0} exceeds outstanding amount {1} for invoice {2}")
                    .format(self.amount, outstanding, self.reference_invoice))

    def on_submit(self):
        # 1. Update Customer Ledger (Credit)
        from vj_biofuel.vj_bio_fuel.accounts_utils import update_customer_ledger, update_invoice_outstanding
        update_customer_ledger(
            customer=self.customer,
            amount=self.amount,
            reference_doctype="Payment Entry",
            reference_name=self.name,
            posting_date=self.posting_date,
            is_debit=False,
            remarks=f"Payment received: {self.name} via {self.mode_of_payment}"
        )
        
        # 2. Update Invoice Outstanding
        if self.reference_invoice:
            update_invoice_outstanding(self.reference_invoice)

    def on_cancel(self):
        # 1. Reverse Ledger (Debit)
        from vj_biofuel.vj_bio_fuel.accounts_utils import update_customer_ledger, update_invoice_outstanding
        update_customer_ledger(
            customer=self.customer,
            amount=self.amount,
            reference_doctype="Payment Entry",
            reference_name=self.name,
            posting_date=self.posting_date,
            is_debit=True,
            remarks=f"Payment cancelled: {self.name}"
        )
        
        # 2. Update Invoice Outstanding
        if self.reference_invoice:
            update_invoice_outstanding(self.reference_invoice)
