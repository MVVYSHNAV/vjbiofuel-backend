# -*- coding: utf-8 -*-
import frappe
from frappe import _
from frappe.utils import flt

def get_current_stock(item, warehouse):
    """Returns latest balance_qty from ledger for an item in a specific warehouse."""
    latest_entry = frappe.db.get_value("Stock Ledger Entry", 
        {"item": item, "warehouse": warehouse}, 
        "balance_qty", 
        order_by="creation desc")
    return flt(latest_entry)

def update_stock(item, warehouse, qty, entry_type, reference_doctype, reference_name, posting_date):
    """
    Central function to update stock via Stock Ledger Entries.
    qty is always positive.
    entry_type = "IN" or "OUT"
    """
    qty = flt(qty)
    if qty <= 0:
        frappe.throw(_("Quantity must be positive for stock update"))

    current_balance = get_current_stock(item, warehouse)
    
    qty_in = 0
    qty_out = 0
    new_balance = current_balance

    if entry_type == "IN":
        qty_in = qty
        new_balance += qty
    elif entry_type == "OUT":
        if current_balance < qty:
            frappe.throw(_("Insufficient stock for Item {0} in Warehouse {1}. Current: {2}, Required: {3}")
                .format(item, warehouse, current_balance, qty))
        qty_out = qty
        new_balance -= qty
    else:
        frappe.throw(_("Invalid entry type: {0}").format(entry_type))

    # Insert Stock Ledger Entry
    sle = frappe.get_doc({
        "doctype": "Stock Ledger Entry",
        "item": item,
        "warehouse": warehouse,
        "qty_in": qty_in,
        "qty_out": qty_out,
        "balance_qty": new_balance,
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "posting_date": posting_date
    })
    sle.insert(ignore_permissions=True)
    return sle
