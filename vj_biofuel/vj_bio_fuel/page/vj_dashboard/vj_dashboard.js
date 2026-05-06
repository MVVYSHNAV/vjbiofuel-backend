frappe.pages['vj_dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'VJ Bio Fuel Dashboard',
		single_column: true
	});

	frappe.dashboard = new VJDashboard(wrapper);
}

class VJDashboard {
	constructor(wrapper) {
		this.wrapper = $(wrapper);
		this.page = wrapper.page;
		this.init();
	}

	init() {
		this.setup_layout();
		this.refresh();
	}

	setup_layout() {
		this.wrapper.find('.page-content').html(`
			<div class="vj-dashboard-container p-4">
				<div class="row" id="metric-cards">
					<!-- Cards will be injected here -->
				</div>
				<div class="row mt-4">
					<div class="col-md-6">
						<div class="card p-3">
							<h5>Top 5 Customers</h5>
							<div id="top-customers-list"></div>
						</div>
					</div>
					<div class="col-md-6">
						<div class="card p-3">
							<h5>Low Stock Alerts</h5>
							<div id="low-stock-list"></div>
						</div>
					</div>
				</div>
			</div>
		`);
	}

	refresh() {
		frappe.call({
			method: 'vj_biofuel.vj_bio_fuel.dashboard_utils.get_all_dashboard_data',
			callback: (r) => {
				if (r.message) {
					this.render_metrics(r.message);
				}
			}
		});
	}

	render_metrics(data) {
		const metrics = [
			{ label: 'Sales Today', value: frappe.format(data.sales.total_sales_today, { fieldtype: 'Currency' }), color: 'blue' },
			{ label: 'Raw Stock', value: `${data.inventory.current_raw_stock} L`, color: 'green' },
			{ label: 'Avg Yield', value: `${data.processing.average_yield_percentage}%`, color: 'orange' },
			{ label: 'Outstanding', value: frappe.format(data.finance.outstanding_amount, { fieldtype: 'Currency' }), color: 'red' }
		];

		let cards_html = metrics.map(m => `
			<div class="col-md-3 mb-4">
				<div class="card p-3 text-center border-left" style="border-left: 5px solid ${m.color} !important;">
					<div class="text-muted small">${m.label}</div>
					<div class="h4 mt-1">${m.value}</div>
				</div>
			</div>
		`).join('');

		this.wrapper.find('#metric-cards').html(cards_html);

		// Render Lists
		let customers_html = data.sales.top_customers.map(c => `
			<div class="d-flex justify-content-between border-bottom py-2">
				<span>${c.customer}</span>
				<span class="font-weight-bold">${frappe.format(c.total, { fieldtype: 'Currency' })}</span>
			</div>
		`).join('') || '<p class="text-muted">No data</p>';
		this.wrapper.find('#top-customers-list').html(customers_html);

		let stock_html = data.inventory.low_stock_items.map(s => `
			<div class="d-flex justify-content-between border-bottom py-2">
				<span>${s.item_code} (${s.warehouse})</span>
				<span class="text-danger font-weight-bold">${s.balance} L</span>
			</div>
		`).join('') || '<p class="text-success">Stock levels healthy</p>';
		this.wrapper.find('#low-stock-list').html(stock_html);
	}
}
