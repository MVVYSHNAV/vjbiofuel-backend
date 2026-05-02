// Copyright (c) 2026, VJ Bio Fuel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        // Any refresh logic
    },
    customer: function(frm) {
        if (frm.doc.customer) {
            frappe.db.get_value('Customer', frm.doc.customer, 'state', (r) => {
                if (r && r.state) {
                    frm.set_value('place_of_supply', r.state);
                }
            });
        }
    },
    company: function(frm) {
        calculate_totals(frm);
    }
});

frappe.ui.form.on('Sales Invoice Item', {
    item: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item) {
            frappe.db.get_value('Item', row.item, 'tax_rate', (r) => {
                if (r && r.tax_rate) {
                    frappe.model.set_value(cdt, cdn, 'tax_rate', r.tax_rate);
                }
            });
        }
    },
    qty: function(frm, cdt, cdn) {
        calculate_item_amount(frm, cdt, cdn);
    },
    rate: function(frm, cdt, cdn) {
        calculate_item_amount(frm, cdt, cdn);
    },
    items_remove: function(frm) {
        calculate_totals(frm);
    }
});

let calculate_item_amount = function(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let amount = flt(row.qty) * flt(row.rate);
    frappe.model.set_value(cdt, cdn, 'amount', flt(amount, 2));
    calculate_totals(frm);
};

let calculate_totals = function(frm) {
    let total_amount = 0;
    let total_tax = 0;
    let cgst_amount = 0;
    let sgst_amount = 0;
    let igst_amount = 0;

    // Fetch tax type based on company and customer state
    // For JS, we'll do a simple check or wait for backend.
    // Let's assume we can fetch it if both are set.
    
    if (frm.doc.company && (frm.doc.place_of_supply || frm.doc.customer)) {
        frappe.db.get_value('Company', frm.doc.company, 'state', (r) => {
            let company_state = r ? r.state : null;
            let customer_state = frm.doc.place_of_supply;
            
            let tax_type = (company_state === customer_state) ? "CGST_SGST" : "IGST";
            frm.set_value('tax_type', tax_type);

            (frm.doc.items || []).forEach(item => {
                let item_amount = flt(item.amount, 2);
                total_amount += item_amount;
                
                let tax_rate = flt(item.tax_rate || 18.0);
                let item_tax = flt((item_amount * tax_rate) / 100.0, 2);
                
                if (tax_type === "IGST") {
                    igst_amount += item_tax;
                } else {
                    cgst_amount += flt(item_tax / 2, 2);
                    sgst_amount += flt(item_tax / 2, 2);
                }
            });

            frm.set_value('total_amount', flt(total_amount, 2));
            frm.set_value('cgst_amount', flt(cgst_amount, 2));
            frm.set_value('sgst_amount', flt(sgst_amount, 2));
            frm.set_value('igst_amount', flt(igst_amount, 2));
            
            if (tax_type === "CGST_SGST") {
                total_tax = cgst_amount + sgst_amount;
            } else {
                total_tax = igst_amount;
            }
            
            frm.set_value('tax_amount', flt(total_tax, 2));
            frm.set_value('grand_total', flt(total_amount + total_tax, 2));
        });
    }
};
