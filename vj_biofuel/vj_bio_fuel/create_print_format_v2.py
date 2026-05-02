import frappe

def create_print_format():
    html_content = """
<style>
    .print-format {
        font-family: 'Arial', sans-serif;
        font-size: 10pt;
        color: #000;
        padding: 5mm;
    }
    .main-table {
        width: 100%;
        border: 1px solid #000;
        border-collapse: collapse;
    }
    .main-table td, .main-table th {
        border: 1px solid #000;
        padding: 5px;
        vertical-align: top;
    }
    .no-border { border: none !important; }
    .bold { font-weight: bold; }
    .text-center { text-align: center; }
    .text-right { text-align: right; }
    .header-title {
        font-size: 12pt;
        text-decoration: underline;
        margin-bottom: 5px;
    }
    .item-table th {
        background-color: #f2f2f2;
    }
    .hsn-table {
        width: 100%;
        margin-top: 10px;
        border-collapse: collapse;
    }
    .hsn-table th, .hsn-table td {
        border: 1px solid #000;
        padding: 3px;
        font-size: 9pt;
    }
</style>

<div class="print-format">
    <div class="text-center bold header-title">Tax Invoice</div>
    
    <table class="main-table">
        <!-- Row 1: Company and Invoice Details -->
        <tr>
            <td width="50%" rowspan="3">
                {% set company = frappe.get_doc("Company", doc.company) %}
                <div class="bold">{{ company.company_name }}</div>
                <div>KINFRA TEXTILE CENTRE</div>
                <div>NADUKANI</div>
                <div>PALLIVAYAL</div>
                <div>GSTIN/UIN: {{ company.gstin or 'N/A' }}</div>
                <div>State Name: {{ company.state or 'N/A' }}, Code : 32</div>
            </td>
            <td width="25%">
                <div style="font-size: 8pt;">Invoice No.</div>
                <div class="bold">{{ doc.name }}</div>
            </td>
            <td width="25%">
                <div style="font-size: 8pt;">e-Way Bill No.</div>
                <div class="bold">{{ doc.e_way_bill_no or '' }}</div>
            </td>
            <td width="25%">
                <div style="font-size: 8pt;">Dated</div>
                <div class="bold">{{ frappe.utils.getdate(doc.posting_date).strftime('%d-%b-%y') }}</div>
            </td>
        </tr>
        <tr>
            <td width="25%">
                <div style="font-size: 8pt;">Delivery Note</div>
                <div>{{ doc.delivery_note or '' }}</div>
            </td>
            <td colspan="2">
                <div style="font-size: 8pt;">Mode/Terms of Payment</div>
                <div>{{ doc.mode_of_payment or '' }}</div>
            </td>
        </tr>
        <tr>
            <td width="25%">
                <div style="font-size: 8pt;">Reference No. & Date.</div>
                <div>{{ doc.reference_no or '' }}</div>
            </td>
            <td colspan="2">
                <div style="font-size: 8pt;">Other References</div>
                <div>{{ doc.other_references or '' }}</div>
            </td>
        </tr>
        
        <!-- Row 2: Consignee and Buyer Order -->
        <tr>
            <td width="50%" rowspan="2">
                {% set customer = frappe.get_doc("Customer", doc.customer) %}
                <div style="font-size: 8pt;">Consignee (Ship to)</div>
                <div class="bold">{{ customer.customer_name }}</div>
                <div>{{ customer.address or '' }}</div>
                <div>GSTIN/UIN : {{ doc.gstin or 'N/A' }}</div>
                <div>State Name : {{ doc.place_of_supply or 'N/A' }}, Code : 37</div>
            </td>
            <td width="25%">
                <div style="font-size: 8pt;">Buyer's Order No.</div>
                <div>{{ doc.buyer_order_no or '' }}</div>
            </td>
            <td colspan="2">
                <div style="font-size: 8pt;">Dated</div>
                <div>{{ doc.buyer_order_date or '' }}</div>
            </td>
        </tr>
        <tr>
            <td width="25%">
                <div style="font-size: 8pt;">Dispatch Doc No.</div>
                <div>{{ doc.dispatch_doc_no or '' }}</div>
            </td>
            <td colspan="2">
                <div style="font-size: 8pt;">Delivery Note Date</div>
                <div>{{ doc.delivery_note_date or '' }}</div>
            </td>
        </tr>

        <!-- Row 3: Buyer and Dispatch Info -->
        <tr>
            <td width="50%" rowspan="2">
                <div style="font-size: 8pt;">Buyer (Bill to)</div>
                <div class="bold">{{ customer.customer_name }}</div>
                <div>{{ customer.address or '' }}</div>
                <div>GSTIN/UIN : {{ doc.gstin or 'N/A' }}</div>
                <div>State Name : {{ doc.place_of_supply or 'N/A' }}, Code : 37</div>
            </td>
            <td width="25%">
                <div style="font-size: 8pt;">Dispatched through</div>
                <div>{{ doc.dispatched_through or '' }}</div>
            </td>
            <td colspan="2">
                <div style="font-size: 8pt;">Destination</div>
                <div>{{ doc.destination or '' }}</div>
            </td>
        </tr>
        <tr>
            <td colspan="3">
                <div style="font-size: 8pt;">Terms of Delivery</div>
                <div>{{ doc.terms_of_delivery or '' }}</div>
            </td>
        </tr>
    </table>

    <!-- Item Table -->
    <table class="main-table" style="margin-top: -1px;">
        <thead>
            <tr>
                <th width="5%">SI No.</th>
                <th width="45%">Description of Goods</th>
                <th width="10%">HSN/SAC</th>
                <th width="10%" class="text-right">Quantity</th>
                <th width="10%" class="text-right">Rate</th>
                <th width="5%">per</th>
                <th width="15%" class="text-right">Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
            <tr>
                <td class="text-center">{{ loop.index }}</td>
                <td>
                    <div class="bold">{{ item.item }}</div>
                    <br>
                    {% if doc.tax_type == "IGST" %}
                        <div class="text-right"><i>OUTPUT IGST {{ item.tax_rate }}%</i></div>
                    {% else %}
                        <div class="text-right"><i>OUTPUT CGST {{ item.tax_rate / 2 }}%</i></div>
                        <div class="text-right"><i>OUTPUT SGST {{ item.tax_rate / 2 }}%</i></div>
                    {% endif %}
                </td>
                <td>{{ item.hsn_code or '' }}</td>
                <td class="text-right bold">{{ item.qty }} LTR</td>
                <td class="text-right">{{ frappe.format(item.rate, "Currency") }}</td>
                <td>LTR</td>
                <td class="text-right bold">{{ frappe.format(item.amount + (doc.tax_amount if loop.last else 0), "Currency") if loop.length == 1 else frappe.format(item.amount, "Currency") }}</td>
            </tr>
            {% if loop.last and loop.length == 1 %}
            <!-- Single item tax row representation like in PDF -->
            <tr>
                <td colspan="6" class="text-right bold">Total</td>
                <td class="text-right bold" style="border-top: 2px solid #000;">₹ {{ frappe.format(doc.grand_total, "Currency") }}</td>
            </tr>
            {% endif %}
            {% endfor %}
            
            {% if doc.items|length > 1 %}
            <tr>
                <td colspan="3" class="text-right bold">Total</td>
                <td class="text-right bold">{{ doc.items | sum(attribute='qty') }} LTR</td>
                <td colspan="2"></td>
                <td class="text-right bold">₹ {{ frappe.format(doc.grand_total, "Currency") }}</td>
            </tr>
            {% endif %}
        </tbody>
    </table>

    <div style="border: 1px solid #000; border-top: none; padding: 5px;">
        <div>Amount Chargeable (in words) <span class="text-right" style="float: right;">E. & O.E</span></div>
        <div class="bold">{{ frappe.utils.money_in_words(doc.grand_total, "INR") }}</div>
    </div>

    <!-- HSN Summary Table -->
    <table class="hsn-table">
        <thead>
            <tr>
                <th rowspan="2">HSN/SAC</th>
                <th rowspan="2">Taxable Value</th>
                {% if doc.tax_type == "IGST" %}
                <th colspan="2">IGST</th>
                {% else %}
                <th colspan="2">CGST</th>
                <th colspan="2">SGST</th>
                {% endif %}
                <th rowspan="2">Total Tax Amount</th>
            </tr>
            <tr>
                <th>Rate</th>
                <th>Amount</th>
                {% if doc.tax_type != "IGST" %}
                <th>Rate</th>
                <th>Amount</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% set hsn_groups = {} %}
            {% for item in doc.items %}
                {% set hsn = item.hsn_code or 'N/A' %}
                {% if hsn not in hsn_groups %}
                    {% set _ = hsn_groups.update({hsn: {'taxable': 0, 'tax': 0, 'rate': item.tax_rate}}) %}
                {% endif %}
                {% set _ = hsn_groups[hsn].update({'taxable': hsn_groups[hsn].taxable + item.amount}) %}
            {% endfor %}
            
            {% for hsn, data in hsn_groups.items() %}
            <tr>
                <td>{{ hsn }}</td>
                <td class="text-right">{{ frappe.format(data.taxable, "Currency") }}</td>
                {% if doc.tax_type == "IGST" %}
                <td class="text-center">{{ data.rate }}%</td>
                <td class="text-right">{{ frappe.format(doc.igst_amount, "Currency") }}</td>
                <td class="text-right">{{ frappe.format(doc.igst_amount, "Currency") }}</td>
                {% else %}
                <td class="text-center">{{ data.rate / 2 }}%</td>
                <td class="text-right">{{ frappe.format(doc.cgst_amount, "Currency") }}</td>
                <td class="text-center">{{ data.rate / 2 }}%</td>
                <td class="text-right">{{ frappe.format(doc.sgst_amount, "Currency") }}</td>
                <td class="text-right">{{ frappe.format(doc.tax_amount, "Currency") }}</td>
                {% endif %}
            </tr>
            {% endfor %}
            <tr class="bold">
                <td class="text-right">Total</td>
                <td class="text-right">{{ frappe.format(doc.total_amount, "Currency") }}</td>
                {% if doc.tax_type == "IGST" %}
                <td></td>
                <td class="text-right">{{ frappe.format(doc.igst_amount, "Currency") }}</td>
                <td class="text-right">{{ frappe.format(doc.igst_amount, "Currency") }}</td>
                {% else %}
                <td></td>
                <td class="text-right">{{ frappe.format(doc.cgst_amount, "Currency") }}</td>
                <td></td>
                <td class="text-right">{{ frappe.format(doc.sgst_amount, "Currency") }}</td>
                <td class="text-right">{{ frappe.format(doc.tax_amount, "Currency") }}</td>
                {% endif %}
            </tr>
        </tbody>
    </table>

    <div style="margin-top: 5px; font-size: 9pt;">
        Tax Amount (in words) : <span class="bold">{{ frappe.utils.money_in_words(doc.tax_amount, "INR") }}</span>
    </div>

    <div style="margin-top: 20px; border: 1px solid #000; padding: 5px;">
        <table width="100%" class="no-border">
            <tr>
                <td width="50%" class="no-border">
                    <div style="text-decoration: underline;">Declaration</div>
                    <div style="font-size: 8pt;">
                        We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.
                    </div>
                </td>
                <td width="50%" class="text-right no-border">
                    <div class="bold">for {{ company.company_name }}</div>
                    <br><br><br>
                    <div class="bold">Authorised Signatory</div>
                </td>
            </tr>
        </table>
    </div>
    
    <div class="text-center" style="font-size: 8pt; margin-top: 10px;">
        This is a Computer Generated Invoice
    </div>
</div>
"""
    
    doc = frappe.get_doc("Print Format", "VJ Sales Invoice")
    doc.html = html_content
    doc.save()
    print("Print Format 'VJ Sales Invoice' updated to match PDF layout.")

if __name__ == "__main__":
    create_print_format()
