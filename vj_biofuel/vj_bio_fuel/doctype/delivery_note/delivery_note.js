// Copyright (c) 2026, VJ Bio Fuel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            if (frm.doc.status === "Dispatched") {
                frm.add_custom_button(__('Mark as In Transit'), () => {
                    frm.call('update_status', { new_status: 'In Transit' }).then(() => frm.reload_doc());
                });
            }
            if (frm.doc.status === "In Transit") {
                frm.add_custom_button(__('Mark as Delivered'), () => {
                    frm.call('update_status', { new_status: 'Delivered' }).then(() => frm.reload_doc());
                });
            }
        }
        
        // UX Improvement: Make phone number clickable
        if (frm.doc.driver_phone && /^\d{10}$/.test(frm.doc.driver_phone)) {
            frm.set_df_property('driver_phone', 'description', 
                `<a href="tel:${frm.doc.driver_phone}" class="text-primary font-weight-bold">📞 Call Driver</a>`
            );
        }
    },
    
    driver_phone: function(frm) {
        if (frm.doc.driver_phone && /^\d{10}$/.test(frm.doc.driver_phone)) {
            frm.set_df_property('driver_phone', 'description', 
                `<a href="tel:${frm.doc.driver_phone}" class="text-primary font-weight-bold">📞 Call Driver</a>`
            );
        } else {
            frm.set_df_property('driver_phone', 'description', __('Enter 10-digit mobile number'));
        }
    },
    
    sales_invoice: function(frm) {
        if (frm.doc.sales_invoice) {
            frappe.model.with_doc('Sales Invoice', frm.doc.sales_invoice, function() {
                let si = frappe.model.get_doc('Sales Invoice', frm.doc.sales_invoice);
                
                frm.clear_table('items');
                si.items.forEach(si_item => {
                    let row = frm.add_child('items');
                    row.item = si_item.item;
                    row.qty = si_item.qty;
                    row.rate = si_item.rate;
                    row.amount = si_item.amount;
                });
                frm.refresh_field('items');
                frm.set_value('customer', si.customer);
            });
        }
    }
});
