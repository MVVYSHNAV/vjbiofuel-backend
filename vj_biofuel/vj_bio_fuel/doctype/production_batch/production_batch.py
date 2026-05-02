import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from vj_biofuel.vj_bio_fuel.stock_utils import update_stock, get_current_stock

class ProductionBatch(Document):
    def validate(self):
        self.calculate_yield()
        self.calculate_costs()
        self.validate_quantities()

    def calculate_yield(self):
        """Calculate wastage and yield percentage"""
        if flt(self.input_qty) > 0:
            self.wastage_qty = flt(self.input_qty) - flt(self.output_qty)
            self.yield_percentage = (flt(self.output_qty) / flt(self.input_qty)) * 100.0
        else:
            self.wastage_qty = 0
            self.yield_percentage = 0

    def calculate_costs(self):
        """Fetch average purchase cost of raw oil and calculate batch costs"""
        # Fetch average rate from submitted Purchase Invoices for this item
        avg_rate = frappe.db.sql("""
            select avg(rate) from `tabPurchase Invoice Item`
            where item = %s and docstatus = 1
        """, self.input_item)[0][0] or 0.0
        
        self.input_cost = flt(self.input_qty) * flt(avg_rate)
        if flt(self.output_qty) > 0:
            self.output_cost_per_litre = flt(self.input_cost) / flt(self.output_qty)

    def validate_quantities(self):
        if flt(self.input_qty) <= 0:
            frappe.throw(_("Input quantity must be greater than 0"))
        if flt(self.output_qty) <= 0:
            frappe.throw(_("Output quantity must be greater than 0"))
        if flt(self.output_qty) > flt(self.input_qty):
            frappe.throw(_("Output quantity cannot exceed input quantity"))
        if flt(self.wastage_qty) < 0:
            frappe.throw(_("Wastage cannot be negative"))

    def on_submit(self):
        self.status = "Submitted"
        
        # 1. Consume Raw Oil (OUT from Raw Oil Warehouse)
        update_stock(
            item=self.input_item,
            warehouse="Raw Oil Warehouse",
            qty=self.input_qty,
            entry_type="OUT",
            reference_doctype="Production Batch",
            reference_name=self.name,
            posting_date=self.posting_date
        )

        # 2. Produce Processed Oil (IN to Processed Oil Warehouse)
        update_stock(
            item=self.output_item,
            warehouse="Processed Oil Warehouse",
            qty=self.output_qty,
            entry_type="IN",
            reference_doctype="Production Batch",
            reference_name=self.name,
            posting_date=self.posting_date
        )

    def on_cancel(self):
        self.status = "Cancelled"

        # Reverse Stock: 
        # 1. Add back Raw Oil (IN to Raw Oil Warehouse)
        update_stock(
            item=self.input_item,
            warehouse="Raw Oil Warehouse",
            qty=self.input_qty,
            entry_type="IN",
            reference_doctype="Production Batch",
            reference_name=self.name,
            posting_date=self.posting_date
        )

        # 2. Remove Processed Oil (OUT from Processed Oil Warehouse)
        update_stock(
            item=self.output_item,
            warehouse="Processed Oil Warehouse",
            qty=self.output_qty,
            entry_type="OUT",
            reference_doctype="Production Batch",
            reference_name=self.name,
            posting_date=self.posting_date
        )

@frappe.whitelist()
def get_available_stock(item, warehouse):
    return get_current_stock(item, warehouse)
