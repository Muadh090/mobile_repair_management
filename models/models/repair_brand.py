from odoo import models, fields, api

class RepairBrand(models.Model):
    _name = 'repair.brand'
    _description = 'Mobile Brand'
    _order = 'name'
    
    name = fields.Char(string='Brand Name', required=True)
    logo = fields.Binary(string='Brand Logo')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    series_ids = fields.One2many('repair.series', 'brand_id', string='Series')
    model_ids = fields.One2many('repair.model', 'brand_id', string='Models')
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Brand name must be unique!'),
    ]