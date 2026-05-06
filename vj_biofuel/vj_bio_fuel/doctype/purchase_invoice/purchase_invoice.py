import frappe
import re
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from vj_biofuel.vj_bio_fuel.stock_utils import update_stock

class PurchaseInvoice(Document):
    def validate(self):
        self.validate_gstin()
        self.set_tax_type()
        self.calculate_totals()

    def validate_gstin(self):
        if self.supplier_gstin:
            gst_regex = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
            if not re.match(gst_regex, self.supplier_gstin):
                frappe.throw(_("Invalid GSTIN format for {0}").format(self.supplier_gstin))

    def set_tax_type(self):
        if not self.company or not self.supplier:
            return
        company_state = frappe.db.get_value("Company", self.company, "state")
        supplier_state = self.supplier_state or frappe.db.get_value("Supplier", self.supplier, "state")
        
        if not company_state:
            frappe.throw(_("Please set State in Company {0}").format(self.company))

        if company_state == supplier_state:
            self.tax_type = "CGST_SGST"
        else:
            self.tax_type = "IGST"

    def calculate_totals(self):
        total_amount = 0
        total_tax = 0
        self.cgst_amount = 0
        self.sgst_amount = 0
        self.igst_amount = 0

        for item in self.items:
            if flt(item.qty) <= 0:
                frappe.throw(_("Quantity must be greater than 0 for item {0}").format(item.item))
            if flt(item.rate) <= 0:
                frappe.throw(_("Rate must be greater than 0 for item {0}").format(item.item))

            item.amount = flt(item.qty) * flt(item.rate)
            item.amount = flt(item.amount, 2)
            
            tax_rate = flt(frappe.db.get_value("Item", item.item, "tax_rate") or 18.0)
            item_tax = flt((item.amount * tax_rate) / 100.0, 2)
            
            if self.tax_type == "IGST":
                self.igst_amount += item_tax
            else:
                self.cgst_amount += flt(item_tax / 2, 2)
                self.sgst_amount += flt(item_tax / 2, 2)
            
            total_amount += item.amount
            total_tax += item_tax

        self.total_amount = flt(total_amount, 2)
        if self.tax_type == "CGST_SGST":
            self.tax_amount = flt(self.cgst_amount + self.sgst_amount, 2)
        else:
            self.tax_amount = flt(self.igst_amount, 2)
        self.grand_total = flt(self.total_amount + self.tax_amount, 2)

    def on_submit(self):
        """Update stock (IN) on submission"""
        warehouse = "Raw Oil Warehouse" # As per prompt
        if not frappe.db.exists("Warehouse", warehouse):
            frappe.throw(_("Warehouse {0} does not exist. Please create it first.").format(warehouse))

        for item in self.items:
            update_stock(
                item.item, 
                warehouse, 
                item.qty, 
                "IN", 
                "Purchase Invoice", 
                self.name, 
                self.posting_date
            )

    def on_cancel(self):
        """Reverse stock (OUT) on cancellation"""
        warehouse = "Raw Oil Warehouse"
        for item in self.items:
            update_stock(
                item.item, 
                warehouse, 
                item.qty, 
                "OUT", 
                "Purchase Invoice", 
                self.name, 
                self.posting_date
            )
