odoo.define('mobile_repair_management.repair_dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');

var _t = core._t;

var RepairDashboard = AbstractAction.extend({
    template: 'RepairDashboard',
    
    init: function (parent, action) {
        this._super(parent, action);
        this.data = {};
    },
    
    willStart: function () {
        var self = this;
        return $.when(
            this._super.apply(this, arguments),
            this.loadData()
        );
    },
    
    loadData: function () {
        var self = this;
        return rpc.query({
            model: 'job.card',
            method: 'get_dashboard_data',
            args: [],
        }).then(function (data) {
            self.data = data;
            return data;
        });
    },
    
    start: function () {
        var self = this;
        this._super.apply(this, arguments);
        this.renderCharts();
        return this.loadData().then(function () {
            self.updateKPIs();
        });
    },
    
    updateKPIs: function () {
        var self = this;
        $('.kpi-total-jobs').text(this.data.total_jobs || 0);
        $('.kpi-in-progress').text(this.data.in_progress || 0);
        $('.kpi-completed').text(this.data.completed || 0);
        $('.kpi-revenue').text(this.formatCurrency(this.data.total_revenue || 0));
    },
    
    renderCharts: function () {
        this.renderStatusChart();
        this.renderInspectionChart();
        this.renderDeliveryChart();
        this.renderRevenueChart();
    },
    
    renderStatusChart: function () {
        var canvas = document.getElementById('statusChart');
        if (!canvas) { return; }
        var ctx = canvas.getContext('2d');
        if (window.Chart) {
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Draft', 'Requested', 'Quotation', 'Approved', 'In Progress', 'Completed', 'Rejected'],
                    datasets: [{
                        data: [10, 20, 15, 25, 30, 40, 5],
                        backgroundColor: ['#f0f0f0','#ffeb3b','#2196f3','#4caf50','#3f51b5','#8bc34a','#f44336']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    },
    
    renderInspectionChart: function () {
        var canvas = document.getElementById('inspectionChart');
        if (!canvas) { return; }
        var ctx = canvas.getContext('2d');
        if (window.Chart) {
            new Chart(ctx, {
                type: 'doughnut',
                data: { labels: ['Basic','Detailed','Diagnostic'], datasets: [{ data: [40,35,25], backgroundColor: ['#4CAF50','#2196F3','#FF9800'] }] },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    },
    
    renderDeliveryChart: function () {
        var canvas = document.getElementById('deliveryChart');
        if (!canvas) { return; }
        var ctx = canvas.getContext('2d');
        if (window.Chart) {
            new Chart(ctx, { type: 'polarArea', data: { labels: ['Pickup','Delivery','Courier'], datasets: [{ data: [60,25,15], backgroundColor: ['#4CAF50','#2196F3','#FF9800'] }] }, options: { responsive: true, maintainAspectRatio: false } });
        }
    },
    
    renderRevenueChart: function () {
        var canvas = document.getElementById('revenueChart');
        if (!canvas) { return; }
        var ctx = canvas.getContext('2d');
        if (window.Chart) {
            new Chart(ctx, {
                type: 'bar',
                data: { labels: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], datasets: [{ label: 'Revenue', data: [12000,19000,15000,25000,22000,30000,28000,35000,32000,40000,38000,45000], backgroundColor: '#4CAF50' }] },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
            });
        }
    },
    
    formatCurrency: function(value) {
        try { return value.toLocaleString(undefined, { style: 'currency', currency: 'USD' }); } catch (e) { return value; }
    }
});

core.action_registry.add('repair_dashboard', RepairDashboard);

return RepairDashboard;

});
