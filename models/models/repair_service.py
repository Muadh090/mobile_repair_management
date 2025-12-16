from odoo import models, fields, api

class RepairService(models.Model):
    _name = 'repair.service'
    _description = 'Repair Service'
    
    name = fields.Char(string='Service Name', required=True)
    service_type = fields.Selection([
        ('basic', 'Basic Service'),
        ('premium', 'Premium Service'),
        ('high_end', 'High-end Service'),
        ('motherboard', 'Motherboard Service'),
        ('screen', 'Screen Replacement'),
        ('battery', 'Battery Replacement'),
        ('software', 'Software/OS'),
    ], string='Service Type', required=True)
    price = fields.Float(string='Price', required=True)
    description = fields.Text(string='Description')
    duration = fields.Float(string='Duration (hours)')
    active = fields.Boolean(string='Active', default=True)
    
    product_id = fields.Many2one('product.product', string='Linked Product')