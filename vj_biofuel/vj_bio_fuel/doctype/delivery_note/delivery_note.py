import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today

class DeliveryNote(Document):
    def validate(self):
        self.validate_linkage()
        self.validate_quantities()
        self.validate_transport()

    def validate_linkage(self):
        if not self.sales_invoice:
            frappe.throw(_("Sales Invoice is mandatory"))
        
        # Ensure Sales Invoice is submitted
        si_status = frappe.db.get_value("Sales Invoice", self.sales_invoice, "docstatus")
        if si_status != 1:
            frappe.throw(_("Sales Invoice {0} must be submitted before creating a Delivery Note").format(self.sales_invoice))

    def validate_quantities(self):
        """Ensure delivery quantity does not exceed remaining invoiced quantity"""
        si = frappe.get_doc("Sales Invoice", self.sales_invoice)
        si_items = {item.item: item.qty for item in si.items}

        for item in self.items:
            if item.item not in si_items:
                frappe.throw(_("Item {0} not found in Sales Invoice {1}").format(item.item, self.sales_invoice))
            
            # Sum of all PREVIOUSLY delivered quantities for this item from this SI
            already_delivered = frappe.db.sql("""
                select sum(dni.qty) 
                from `tabDelivery Note Item` dni
                join `tabDelivery Note` dn on dn.name = dni.parent
                where dn.sales_invoice = %s 
                and dni.item = %s 
                and dn.docstatus = 1
                and dn.name != %s
            """, (self.sales_invoice, item.item, self.name or ""))[0][0] or 0.0

            remaining = flt(si_items[item.item]) - flt(already_delivered)
            
            if flt(item.qty) > flt(remaining):
                frappe.throw(_("Cannot deliver {0} L of {1}. Only {2} L remaining in Invoice {3}")
                    .format(item.qty, item.item, remaining, self.sales_invoice))

    def validate_transport(self):
        """Mandatory checks for vehicle and driver info"""
        if not self.vehicle_number:
            frappe.throw(_("Vehicle Number is mandatory for transport tracking"))
        
        if not self.driver_phone:
            frappe.throw(_("Driver Phone Number is mandatory"))
        
        # Phone validation: 10 digits numeric only
        phone = str(self.driver_phone).strip()
        if not (phone.isdigit() and len(phone) == 10):
            frappe.throw(_("Driver Phone Number must be exactly 10 digits (numeric only)"))

    def on_submit(self):
        if self.status == "Draft":
            self.db_set("status", "Dispatched")

    @frappe.whitelist()
    def update_status(self, new_status):
        """Handle status transitions manually via buttons"""
        valid_transitions = {
            "Draft": ["Dispatched"],
            "Dispatched": ["In Transit", "Cancelled"],
            "In Transit": ["Delivered", "Cancelled"],
            "Delivered": []
        }

        if new_status not in valid_transitions.get(self.status, []):
            frappe.throw(_("Invalid status transition from {0} to {1}").format(self.status, new_status))

        self.db_set("status", new_status)
        return self.status
