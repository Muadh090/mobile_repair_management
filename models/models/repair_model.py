from odoo import models, fields, api

class RepairModel(models.Model):
    _name = 'repair.model'
    _description = 'Mobile Model'
    _order = 'name'
    
    name = fields.Char(string='Model Name', required=True)
    brand_id = fields.Many2one('repair.brand', string='Brand', required=True)
    series_id = fields.Many2one('repair.series', string='Series', required=True)
    image = fields.Binary(string='Model Image')
    description = fields.Text(string='Description')
    specifications = fields.Html(string='Specifications')
    common_issues = fields.Html(string='Common Issues')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('name_series_unique', 'unique(name, series_id)', 'Model name must be unique per series!'),
    ]