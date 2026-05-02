import frappe

def run():
    if not frappe.db.exists("VJ Bio Fuel Settings", "VJ Bio Fuel Settings"):
        doc = frappe.get_single("VJ Bio Fuel Settings")
        doc.default_tax_rate = 18.0
        doc.enable_auto_production_batch = 1
        doc.save()
        print("Default VJ Bio Fuel Settings created.")
    else:
        print("VJ Bio Fuel Settings already exists.")

if __name__ == "__main__":
    run()
