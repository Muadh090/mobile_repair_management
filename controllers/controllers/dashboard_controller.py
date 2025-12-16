from odoo import http
from odoo.http import request
import json

class DashboardController(http.Controller):
    
    @http.route('/mobile_repair/dashboard_data', type='json', auth='user')
    def dashboard_data(self):
        JobCard = request.env['job.card']
        
        # State counts
        state_data = JobCard.read_group(
            domain=[],
            fields=['state'],
            groupby=['state']
        )
        
        # Inspection types
        inspection_data = JobCard.read_group(
            domain=[],
            fields=['inspection_type'],
            groupby=['inspection_type']
        )
        
        # Delivery types
        delivery_data = JobCard.read_group(
            domain=[],
            fields=['delivery_type'],
            groupby=['delivery_type']
        )
        
        return {
            'states': state_data,
            'inspections': inspection_data,
            'deliveries': delivery_data,
        }