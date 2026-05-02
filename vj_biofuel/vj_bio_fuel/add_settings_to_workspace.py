import frappe

def run():
    # 1. Update Workspace Links
    workspace = frappe.get_doc("Workspace", "VJ Bio Fuel Admin")
    
    # Check if link already exists
    if not any(l.label == "VJ Bio Fuel Settings" for l in workspace.links):
        workspace.append("links", {
            "label": "VJ Bio Fuel Settings",
            "link_to": "VJ Bio Fuel Settings",
            "link_type": "DocType",
            "type": "Link",
            "icon": "settings",
            "parentfield": "links",
            "parenttype": "Workspace"
        })
        workspace.save()
        print("Settings link added to Workspace.")
    else:
        print("Settings link already exists.")

if __name__ == "__main__":
    run()
