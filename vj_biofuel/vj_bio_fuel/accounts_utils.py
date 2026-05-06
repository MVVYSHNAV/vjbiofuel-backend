import frappe
from frappe.utils import flt

def update_customer_ledger(customer, amount, reference_doctype, reference_name, posting_date, is_debit=True, remarks=""):
    """
    Update customer ledger and return the new balance.
    amount: Positive value
    is_debit: True for Invoice (increase balance), False for Payment (decrease balance)
    """
    # Get previous balance
    prev_balance = frappe.db.get_value("Customer Ledger Entry", 
                                      {"customer": customer}, 
                                      "balance", 
                                      order_by="creation desc") or 0.0
    
    debit = flt(amount) if is_debit else 0.0
    credit = 0.0 if is_debit else flt(amount)
    
    new_balance = flt(prev_balance) + debit - credit
    
    ledger = frappe.get_doc({
        "doctype": "Customer Ledger Entry",
        "customer": customer,
        "posting_date": posting_date,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "debit": debit,
        "credit": credit,
        "balance": new_balance,
        "remarks": remarks
    })
    ledger.insert(ignore_permissions=True)
    return new_balance

def get_invoice_outstanding(invoice_name):
    """Calculate outstanding for a specific invoice"""
    grand_total = frappe.db.get_value("Sales Invoice", invoice_name, "grand_total") or 0.0
    
    # Sum of all submitted payments linked to this invoice
    total_paid = frappe.db.sql("""
        select sum(amount) from `tabPayment Entry`
        where reference_invoice = %s and docstatus = 1
    """, invoice_name)[0][0] or 0.0
    
    return flt(grand_total) - flt(total_paid)

def update_invoice_outstanding(invoice_name):
    """Update the outstanding_amount field in Sales Invoice"""
    outstanding = get_invoice_outstanding(invoice_name)
    frappe.db.set_value("Sales Invoice", invoice_name, "outstanding_amount", outstanding)
    return outstanding

def check_freeze_period(posting_date):
    """
    Check if the posting date is within a frozen period.
    """
    # Simple check: Block anything before 2026-04-01 for this demo
    freeze_date = "2026-04-01" 
    if posting_date <= freeze_date:
        frappe.throw(f"Transactions on or before {freeze_date} are frozen and cannot be modified.")
