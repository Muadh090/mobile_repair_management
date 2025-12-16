from odoo import models, fields, api

class RepairSeries(models.Model):
    _name = 'repair.series'
    _description = 'Mobile Series'
    _order = 'name'
    
    name = fields.Char(string='Series Name', required=True)
    brand_id = fields.Many2one('repair.brand', string='Brand', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    model_ids = fields.One2many('repair.model', 'series_id', string='Models')
    
    _sql_constraints = [
        ('name_brand_unique', 'unique(name, brand_id)', 'Series name must be unique per brand!'),
    ]