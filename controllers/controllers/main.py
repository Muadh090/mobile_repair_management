from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError

class MobileRepairController(http.Controller):
    
    @http.route('/mobile_repair/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self):
        """Return dashboard data for charts"""
        user = request.env.user
        allowed = any([
            user.has_group('mobile_repair_management.group_repair_manager'),
            user.has_group('mobile_repair_management.group_repair_lead'),
            user.has_group('mobile_repair_management.group_repair_technician'),
            user.has_group('mobile_repair_management.group_repair_csr'),
            user.has_group('mobile_repair_management.group_repair_procurement'),
            user.has_group('mobile_repair_management.group_repair_accounting'),
        ])
        if not allowed:
            raise AccessError('Not allowed')

        JobCard = request.env['job.card']
        
        # Total counts by state
        states = JobCard.read_group(
            domain=[],
            fields=['state', 'id:count'],
            groupby=['state']
        )
        
        # Inspection types
        inspections = JobCard.read_group(
            domain=[],
            fields=['inspection_type', 'id:count'],
            groupby=['inspection_type']
        )
        
        # Delivery types
        deliveries = JobCard.read_group(
            domain=[],
            fields=['delivery_type', 'id:count'],
            groupby=['delivery_type']
        )
        
        # Monthly invoiced amounts
        invoices = JobCard.read_group(
            domain=[('invoice_status', '=', 'invoiced')],
            fields=['create_date:month', 'total_amount:sum'],
            groupby=['create_date:month']
        )
        
        return {
            'states': states,
            'inspections': inspections,
            'deliveries': deliveries,
            'invoices': invoices,
        }