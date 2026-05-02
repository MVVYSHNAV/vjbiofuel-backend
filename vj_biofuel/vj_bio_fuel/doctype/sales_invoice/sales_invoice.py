import frappe
import re
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt
from vj_biofuel.vj_bio_fuel.stock_utils import update_stock

class SalesInvoice(Document):
    def validate(self):
        from vj_biofuel.vj_bio_fuel.accounts_utils import check_freeze_period
        check_freeze_period(self.posting_date)
        
        self.validate_gstin()
        self.set_tax_type()
        self.calculate_totals()

    def validate_gstin(self):
        """GSTIN validation using regex for India"""
        if self.gstin:
            gst_regex = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
            if not re.match(gst_regex, self.gstin):
                frappe.throw(_("Invalid GSTIN format for {0}").format(self.gstin))

    def set_tax_type(self):
        """Determine if it's IGST or CGST/SGST based on Company state (source of truth)"""
        if not self.company or not self.customer:
            return

        company_state = frappe.db.get_value("Company", self.company, "state")
        customer_state = self.place_of_supply or frappe.db.get_value("Customer", self.customer, "state")

        if not company_state:
            frappe.throw(_("Please set State in Company {0}").format(self.company))

        if company_state == customer_state:
            self.tax_type = "CGST_SGST"
        else:
            self.tax_type = "IGST"

    def calculate_totals(self):
        """Calculate amount for each item and total invoice amounts with proper rounding and breakup"""
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
            item.amount = flt(item.amount, 2) # Round to 2 decimals
            
            # Fetch tax rate from item
            tax_rate = flt(frappe.db.get_value("Item", item.item, "tax_rate") or 18.0)
            
            item_tax = (item.amount * tax_rate) / 100.0
            item_tax = flt(item_tax, 2) # Round tax to 2 decimals
            
            if self.tax_type == "IGST":
                self.igst_amount += item_tax
            else:
                self.cgst_amount += flt(item_tax / 2, 2)
                self.sgst_amount += flt(item_tax / 2, 2)
            
            total_amount += item.amount
            total_tax += item_tax

        self.total_amount = flt(total_amount, 2)
        self.tax_amount = flt(total_tax, 2)
        
        # Adjust tax_amount based on sum of breakup to avoid rounding mismatch
        if self.tax_type == "CGST_SGST":
            self.tax_amount = flt(self.cgst_amount + self.sgst_amount, 2)
        else:
            self.tax_amount = flt(self.igst_amount, 2)
            
        self.grand_total = flt(self.total_amount + self.tax_amount, 2)

    def on_submit(self):
        """Update stock (OUT) on submission and update customer ledger"""
        warehouse = "Processed Oil Warehouse"
        if not frappe.db.exists("Warehouse", warehouse):
            frappe.throw(_("Warehouse {0} does not exist. Please create it first.").format(warehouse))

        # 1. Update Stock
        for item in self.items:
            update_stock(
                item.item, 
                warehouse, 
                item.qty, 
                "OUT", 
                "Sales Invoice", 
                self.name, 
                self.posting_date or frappe.utils.today()
            )
        
        # 2. Update Customer Ledger
        from vj_biofuel.vj_bio_fuel.accounts_utils import update_customer_ledger, update_invoice_outstanding
        update_customer_ledger(
            customer=self.customer,
            amount=self.grand_total,
            reference_doctype="Sales Invoice",
            reference_name=self.name,
            posting_date=self.posting_date or frappe.utils.today(),
            is_debit=True,
            remarks=f"Invoice submitted: {self.name}"
        )
        
        # 3. Initialize Outstanding
        update_invoice_outstanding(self.name)

    def on_cancel(self):
        """Reverse stock (IN) on cancellation and update customer ledger"""
        warehouse = "Processed Oil Warehouse"
        
        # 1. Reverse Stock
        for item in self.items:
            update_stock(
                item.item, 
                warehouse, 
                item.qty, 
                "IN", 
                "Sales Invoice", 
                self.name, 
                self.posting_date or frappe.utils.today()
            )
        
        # 2. Reverse Ledger (Credit)
        from vj_biofuel.vj_bio_fuel.accounts_utils import update_customer_ledger
        update_customer_ledger(
            customer=self.customer,
            amount=self.grand_total,
            reference_doctype="Sales Invoice",
            reference_name=self.name,
            posting_date=self.posting_date or frappe.utils.today(),
            is_debit=False,
            remarks=f"Invoice cancelled: {self.name}"
        )
        
        # 3. Clear Outstanding
        self.db_set("outstanding_amount", 0)
