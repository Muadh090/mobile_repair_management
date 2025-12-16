from odoo import models, fields, api

class JobCardServiceLine(models.Model):
    _name = 'job.card.service.line'
    _description = 'Job Card Service Line'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True, ondelete='cascade')
    service_id = fields.Many2one('repair.service', string='Service', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', required=True)
    quantity = fields.Float(string='Quantity', default=1)
    price_total = fields.Float(string='Total', compute='_compute_total', store=True)
    
    @api.depends('price', 'quantity')
    def _compute_total(self):
        for line in self:
            line.price_total = line.price * line.quantity

class JobCardPartLine(models.Model):
    _name = 'job.card.part.line'
    _description = 'Job Card Part Line'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', required=True, default=1)
    unit_price = fields.Float(string='Unit Price', required=True)
    price_total = fields.Float(string='Total', compute='_compute_total', store=True)
    stock_available = fields.Float(string='Available Stock', related='product_id.qty_available')
    
    @api.depends('unit_price', 'quantity')
    def _compute_total(self):
        for line in self:
            line.price_total = line.unit_price * line.quantity