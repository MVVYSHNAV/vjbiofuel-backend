import frappe
from frappe.utils import today, date_diff, flt

@frappe.whitelist()
def get_payment_aging_report():
    """
    Returns aging of outstanding invoices:
    0-30, 30-60, 60+ days
    """
    invoices = frappe.get_all("Sales Invoice", 
                             filters={"docstatus": 1, "outstanding_amount": [">", 0]},
                             fields=["name", "customer", "posting_date", "outstanding_amount"])
    
    now = today()
    report = {
        "0_30": 0.0,
        "30_60": 0.0,
        "60_plus": 0.0,
        "details": []
    }

    for inv in invoices:
        diff = date_diff(now, inv.posting_date)
        amount = flt(inv.outstanding_amount)
        
        entry = inv.copy()
        entry["age"] = diff
        
        if diff <= 30:
            report["0_30"] += amount
            entry["bucket"] = "0-30"
        elif diff <= 60:
            report["30_60"] += amount
            entry["bucket"] = "30-60"
        else:
            report["60_plus"] += amount
            entry["bucket"] = "60+"
            
        report["details"].append(entry)

    return report

@frappe.whitelist()
def get_profitability_report():
    """
    Calculates profit per invoice based on production cost vs sales price
    """
    # This is a simplified profit report
    # Profit = Sales Grand Total - (Qty * Production Cost Per Litre)
    
    invoices = frappe.get_all("Sales Invoice", 
                             filters={"docstatus": 1},
                             fields=["name", "customer", "posting_date", "grand_total"])
    
    report_data = []
    total_profit = 0.0

    for inv in invoices:
        items = frappe.get_all("Sales Invoice Item", 
                              filters={"parent": inv.name}, 
                              fields=["item", "qty", "amount"])
        
        inv_cost = 0.0
        for item in items:
            # Get latest production cost for this item
            prod_cost = frappe.db.get_value("Production Batch", 
                                          {"output_item": item.item, "status": "Submitted"}, 
                                          "output_cost_per_litre", 
                                          order_by="posting_date desc") or 0.0
            inv_cost += flt(item.qty) * flt(prod_cost)
        
        profit = flt(inv.grand_total) - inv_cost
        total_profit += profit
        
        report_data.append({
            "invoice": inv.name,
            "customer": inv.customer,
            "revenue": inv.grand_total,
            "cost": inv_cost,
            "profit": profit
        })

    return {
        "total_profit": total_profit,
        "details": report_data
    }
