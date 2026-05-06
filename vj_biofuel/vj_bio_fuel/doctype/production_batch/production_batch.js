// Copyright (c) 2026, VJ Bio Fuel and contributors
// For license information, please see license.txt

frappe.ui.form.on('Production Batch', {
    onload: function(frm) {
        if (frm.is_new()) {
            frm.set_value('input_item', 'Raw Waste Oil');
            frm.set_value('output_item', 'Processed Oil');
        }
    },
    input_item: function(frm) {
        fetch_stock(frm);
    },
    input_qty: function(frm) {
        calculate_yield(frm);
    },
    output_qty: function(frm) {
        calculate_yield(frm);
    }
});

let fetch_stock = function(frm) {
    if (frm.doc.input_item) {
        frappe.call({
            method: "vj_biofuel.vj_bio_fuel.doctype.production_batch.production_batch.get_available_stock",
            args: {
                item: frm.doc.input_item,
                warehouse: "Raw Oil Warehouse"
            },
            callback: function(r) {
                if (r.message !== undefined) {
                    frm.set_value('available_stock', r.message);
                }
            }
        });
    }
};

let calculate_yield = function(frm) {
    let input_qty = flt(frm.doc.input_qty);
    let output_qty = flt(frm.doc.output_qty);
    
    if (input_qty > 0) {
        let wastage = input_qty - output_qty;
        let yield_pct = (output_qty / input_qty) * 100.0;
        
        frm.set_value('wastage_qty', flt(wastage, 2));
        frm.set_value('yield_percentage', flt(yield_pct, 2));
        
        if (yield_pct < 50) {
            frappe.msgprint(__("Warning: Yield is low ({0}%). Please verify quantities.", [flt(yield_pct, 2)]));
        }
    }
};
