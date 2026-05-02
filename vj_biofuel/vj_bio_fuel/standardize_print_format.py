import frappe

def create_print_format():
    html_content = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .print-format {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 9pt;
        color: #000;
        line-height: 1.4;
        padding: 0;
    }
    
    .main-table {
        width: 100%;
        border: 1.5px solid #000;
        border-collapse: collapse;
    }
    
    .main-table td, .main-table th {
        border: 1px solid #000;
        padding: 6px 8px;
        vertical-align: top;
    }
    
    .bold { font-weight: 700; }
    .semibold { font-weight: 600; }
    .text-center { text-align: center; }
    .text-right { text-align: right; }
    .text-uppercase { text-transform: uppercase; }
    
    .invoice-header {
        font-size: 14pt;
        letter-spacing: 1px;
        padding: 10px 0;
        border-bottom: 1.5px solid #000;
    }
    
    .label-small {
        font-size: 7.5pt;
        color: #333;
        margin-bottom: 2px;
        display: block;
    }
    
    .item-table th {
        background-color: #f8f9fa;
        text-transform: uppercase;
        font-size: 8.5pt;
    }
    
    .hsn-summary-table {
        width: 100%;
        margin-top: 15px;
        border-collapse: collapse;
        border: 1px solid #000;
    }
    
    .hsn-summary-table th, .hsn-summary-table td {
        border: 1px solid #000;
        padding: 4px 6px;
        font-size: 8.5pt;
    }
    
    .amount-words {
        padding: 10px;
        border: 1.5px solid #000;
        border-top: none;
        background-color: #fff;
    }
    
    .footer-box {
        margin-top: 20px;
        border: 1.5px solid #000;
    }
    
    .signature-area {
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 10px;
    }
</style>

<div class="print-format">
    <div class="text-center bold text-uppercase invoice-header">Tax Invoice</div>
    
    <table class="main-table">
        <!-- Section 1: Company and Metadata -->
        <tr>
            <td width="50%" rowspan="3">
                {% set company = frappe.get_doc("Company", doc.company) %}
                <div class="bold" style="font-size: 12pt;">{{ company.company_name }}</div>
                <div style="margin-top: 5px;">
                    KINFRA TEXTILE CENTRE, NADUKANI<br>
                    PALLIVAYAL, KERALA - 670642<br>
                    <span class="semibold">GSTIN/UIN:</span> {{ company.gstin or 'N/A' }}<br>
                    <span class="semibold">State:</span> {{ company.state or 'N/A' }} (Code: 32)
                </div>
            </td>
            <td width="25%">
                <span class="label-small">Invoice No.</span>
                <div class="bold">{{ doc.name }}</div>
            </td>
            <td width="25%">
                <span class="label-small">Dated</span>
                <div class="bold">{{ frappe.utils.getdate(doc.posting_date).strftime('%d-%b-%Y') }}</div>
            </td>
        </tr>
        <tr>
            <td>
                <span class="label-small">Delivery Note</span>
                <div>{{ doc.delivery_note or '--' }}</div>
            </td>
            <td>
                <span class="label-small">Mode/Terms of Payment</span>
                <div>{{ doc.mode_of_payment or '--' }}</div>
            </td>
        </tr>
        <tr>
            <td>
                <span class="label-small">Reference No. & Date</span>
                <div>{{ doc.reference_no or '--' }}</div>
            </td>
            <td>
                <span class="label-small">Other References</span>
                <div>{{ doc.other_references or '--' }}</div>
            </td>
        </tr>
        
        <!-- Section 2: Consignee and Buyer -->
        <tr>
            <td width="50%" rowspan="2">
                {% set customer = frappe.get_doc("Customer", doc.customer) %}
                <span class="label-small">Consignee (Ship to)</span>
                <div class="bold">{{ customer.customer_name }}</div>
                <div>
                    {{ customer.address or 'Address not available' }}<br>
                    <span class="semibold">GSTIN/UIN:</span> {{ doc.gstin or 'N/A' }}<br>
                    <span class="semibold">State:</span> {{ doc.place_of_supply or 'N/A' }}
                </div>
            </td>
            <td>
                <span class="label-small">Buyer's Order No.</span>
                <div>{{ doc.buyer_order_no or '--' }}</div>
            </td>
            <td>
                <span class="label-small">Dated</span>
                <div>{{ doc.buyer_order_date or '--' }}</div>
            </td>
        </tr>
        <tr>
            <td>
                <span class="label-small">Dispatch Doc No.</span>
                <div>{{ doc.dispatch_doc_no or '--' }}</div>
            </td>
            <td>
                <span class="label-small">Dispatched through</span>
                <div>{{ doc.dispatched_through or '--' }}</div>
            </td>
        </tr>

        <tr>
            <td width="50%">
                <span class="label-small">Buyer (Bill to)</span>
                <div class="bold">{{ customer.customer_name }}</div>
                <div>
                    {{ customer.address or 'Address not available' }}<br>
                    <span class="semibold">GSTIN/UIN:</span> {{ doc.gstin or 'N/A' }}
                </div>
            </td>
            <td colspan="2">
                <span class="label-small">Terms of Delivery</span>
                <div>{{ doc.terms_of_delivery or '--' }}</div>
            </td>
        </tr>
    </table>

    <!-- Item Table -->
    <table class="main-table item-table" style="border-top: none;">
        <thead>
            <tr>
                <th width="5%" class="text-center">Sl</th>
                <th width="40%">Description of Goods</th>
                <th width="10%" class="text-center">HSN/SAC</th>
                <th width="12%" class="text-right">Quantity</th>
                <th width="12%" class="text-right">Rate</th>
                <th width="6%" class="text-center">Per</th>
                <th width="15%" class="text-right">Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for item in doc.items %}
            <tr>
                <td class="text-center">{{ loop.index }}</td>
                <td>
                    <div class="bold">{{ item.item }}</div>
                    <div style="margin-top: 4px; font-size: 8.5pt;">
                        {% if doc.tax_type == "IGST" %}
                            <i style="color: #444;">OUTPUT IGST {{ item.tax_rate }}%</i>
                        {% else %}
                            <i style="color: #444;">OUTPUT CGST {{ item.tax_rate / 2 }}% + SGST {{ item.tax_rate / 2 }}%</i>
                        {% endif %}
                    </div>
                </td>
                <td class="text-center">{{ item.hsn_code or '--' }}</td>
                <td class="text-right bold">{{ item.qty }} LTR</td>
                <td class="text-right">{{ frappe.format(item.rate, "Currency") }}</td>
                <td class="text-center">LTR</td>
                <td class="text-right bold">{{ frappe.format(item.amount, "Currency") }}</td>
            </tr>
            {% endfor %}
            
            <!-- Filler rows to maintain height if needed -->
            {% if doc.items|length < 3 %}
            <tr style="height: 40px;"><td colspan="7"></td></tr>
            {% endif %}

            <!-- Total Row -->
            <tr style="background-color: #f8f9fa;">
                <td colspan="3" class="text-right bold">Total</td>
                <td class="text-right bold">{{ doc.items | sum(attribute='qty') }} LTR</td>
                <td colspan="2"></td>
                <td class="text-right bold" style="font-size: 10.5pt;">₹ {{ frappe.format(doc.grand_total, "Currency") }}</td>
            </tr>
        </tbody>
    </table>

    <!-- Amount in Words -->
    <div class="amount-words">
        <span class="label-small">Amount Chargeable (in words)</span>
        <div class="bold" style="text-transform: capitalize; font-size: 9.5pt;">
            INR {{ frappe.utils.money_in_words(doc.grand_total, "INR").replace("INR ", "") }} Only
            <span style="float: right; font-weight: normal; font-size: 8pt;">E. & O.E</span>
        </div>
    </div>

    <!-- HSN Summary -->
    <table class="hsn-summary-table">
        <thead>
            <tr style="background-color: #f8f9fa;">
                <th rowspan="2">HSN/SAC</th>
                <th rowspan="2">Taxable Value</th>
                {% if doc.tax_type == "IGST" %}
                    <th colspan="2">Integrated Tax</th>
                {% else %}
                    <th colspan="2">Central Tax</th>
                    <th colspan="2">State Tax</th>
                {% endif %}
                <th rowspan="2">Total Tax Amount</th>
            </tr>
            <tr style="background-color: #f8f9fa;">
                <th width="8%">Rate</th><th width="12%">Amount</th>
                {% if doc.tax_type != "IGST" %}
                    <th width="8%">Rate</th><th width="12%">Amount</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% set hsn_groups = {} %}
            {% for item in doc.items %}
                {% set hsn = item.hsn_code or 'N/A' %}
                {% if hsn not in hsn_groups %}
                    {% set _ = hsn_groups.update({hsn: {'taxable': 0, 'rate': item.tax_rate}}) %}
                {% endif %}
                {% set _ = hsn_groups[hsn].update({'taxable': hsn_groups[hsn].taxable + item.amount}) %}
            {% endfor %}
            
            {% for hsn, data in hsn_groups.items() %}
            <tr>
                <td class="text-center">{{ hsn }}</td>
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
            <tr class="bold" style="background-color: #f8f9fa;">
                <td class="text-right">Total</td>
                <td class="text-right">{{ frappe.format(doc.total_amount, "Currency") }}</td>
                {% if doc.tax_type == "IGST" %}
                    <td></td><td class="text-right">{{ frappe.format(doc.igst_amount, "Currency") }}</td>
                    <td class="text-right">{{ frappe.format(doc.igst_amount, "Currency") }}</td>
                {% else %}
                    <td></td><td class="text-right">{{ frappe.format(doc.cgst_amount, "Currency") }}</td>
                    <td></td><td class="text-right">{{ frappe.format(doc.sgst_amount, "Currency") }}</td>
                    <td class="text-right">{{ frappe.format(doc.tax_amount, "Currency") }}</td>
                {% endif %}
            </tr>
        </tbody>
    </table>

    <div style="margin-top: 8px; font-size: 8.5pt;">
        Tax Amount (in words) : <span class="bold">INR {{ frappe.utils.money_in_words(doc.tax_amount, "INR").replace("INR ", "") }} Only</span>
    </div>

    <!-- Final Footer -->
    <div class="footer-box">
        <table width="100%" style="border-collapse: collapse;">
            <tr>
                <td width="60%" style="border-right: 1px solid #000; padding: 10px;">
                    <div class="bold" style="text-decoration: underline; margin-bottom: 5px;">Declaration</div>
                    <div style="font-size: 8pt; line-height: 1.3;">
                        We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.
                    </div>
                </td>
                <td width="40%" class="signature-area">
                    <div class="text-right bold" style="font-size: 8.5pt;">for {{ company.company_name }}</div>
                    <div class="text-right bold" style="font-size: 9pt;">Authorised Signatory</div>
                </td>
            </tr>
        </table>
    </div>
    
    <div class="text-center" style="font-size: 7.5pt; margin-top: 15px; color: #666;">
        This is a Computer Generated Invoice. No Signature Required.
    </div>
</div>
"""
    
    doc = frappe.get_doc("Print Format", "VJ Sales Invoice")
    doc.html = html_content
    doc.save()
    print("Print Format 'VJ Sales Invoice' standardized with Inter font and premium spacing.")

if __name__ == "__main__":
    create_print_format()
