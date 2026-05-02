import frappe
from frappe.utils import today, get_first_day, get_last_day, flt

@frappe.whitelist()
def get_sales_summary():
    """Returns sales metrics for today and current month"""
    now = today()
    first_day = get_first_day(now)
    last_day = get_last_day(now)

    # Today's Sales
    sales_today = frappe.db.sql("""
        select sum(grand_total) from `tabSales Invoice`
        where posting_date = %s and docstatus = 1
    """, now)[0][0] or 0.0

    # Monthly Sales
    sales_month = frappe.db.sql("""
        select sum(grand_total) from `tabSales Invoice`
        where posting_date between %s and %s and docstatus = 1
    """, (first_day, last_day))[0][0] or 0.0

    # Top 5 Customers
    top_customers = frappe.db.sql("""
        select customer, sum(grand_total) as total
        from `tabSales Invoice`
        where docstatus = 1
        group by customer
        order by total desc
        limit 5
    """, as_dict=1)

    return {
        "total_sales_today": flt(sales_today, 2),
        "total_sales_month": flt(sales_month, 2),
        "top_customers": top_customers
    }

@frappe.whitelist()
def get_inventory_summary():
    """Returns current stock levels and low stock items"""
    # Raw Oil Stock
    raw_stock = frappe.db.sql("""
        select sum(actual_qty) from `tabStock Ledger Entry`
        where warehouse = 'Raw Oil Warehouse'
    """)[0][0] or 0.0

    # Processed Oil Stock
    processed_stock = frappe.db.sql("""
        select sum(actual_qty) from `tabStock Ledger Entry`
        where warehouse = 'Processed Oil Warehouse'
    """)[0][0] or 0.0

    # Low Stock Items (Threshold < 1000L)
    low_stock = frappe.db.sql("""
        select item_code, warehouse, sum(actual_qty) as balance
        from `tabStock Ledger Entry`
        group by item_code, warehouse
        having balance < 1000
    """, as_dict=1)

    return {
        "current_raw_stock": flt(raw_stock, 2),
        "current_processed_stock": flt(processed_stock, 2),
        "low_stock_items": low_stock
    }

@frappe.whitelist()
def get_processing_summary():
    """Returns yield and wastage metrics"""
    # Yield and Wastage
    stats = frappe.db.sql("""
        select 
            avg(yield_percentage) as avg_yield,
            sum(wastage_qty) as total_wastage,
            count(name) as batch_count
        from `tabProduction Batch`
        where docstatus = 1
    """, as_dict=1)[0]

    return {
        "average_yield_percentage": flt(stats.avg_yield, 2),
        "total_wastage": flt(stats.total_wastage, 2),
        "batch_count": stats.batch_count
    }

@frappe.whitelist()
def get_financial_summary():
    """Returns receivable and collection metrics"""
    # Total Receivables (Debits in Ledger)
    total_receivables = frappe.db.sql("""
        select sum(debit) from `tabCustomer Ledger Entry`
    """)[0][0] or 0.0

    # Total Collected (Credits in Ledger)
    total_collected = frappe.db.sql("""
        select sum(credit) from `tabCustomer Ledger Entry`
    """)[0][0] or 0.0

    # Outstanding (Current Balance)
    # We can sum all balances or just get sum(debit) - sum(credit)
    outstanding = flt(total_receivables) - flt(total_collected)

    return {
        "total_receivables": flt(total_receivables, 2),
        "total_collected": flt(total_collected, 2),
        "outstanding_amount": flt(outstanding, 2)
    }

@frappe.whitelist()
def get_all_dashboard_data():
    """Helper to fetch all data in one call for the UI with caching"""
    cache_key = "vj_dashboard_all_data"
    cached_data = frappe.cache().get_value(cache_key)
    
    if cached_data:
        return cached_data
    
    data = {
        "sales": get_sales_summary(),
        "inventory": get_inventory_summary(),
        "processing": get_processing_summary(),
        "finance": get_financial_summary()
    }
    
    # Cache for 600 seconds (10 minutes)
    frappe.cache().set_value(cache_key, data, expires_in_sec=600)
    return data
