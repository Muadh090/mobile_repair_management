from odoo import models, fields


class RepairIssueTemplate(models.Model):
    _name = 'repair.issue.template'
    _description = 'Predefined Repair Issue Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True)
    brand_id = fields.Many2one('repair.brand', string='Brand')
    model_id = fields.Many2one('repair.model', string='Model')
    description = fields.Text(string='Description')
    service_line_ids = fields.One2many('repair.issue.template.service', 'template_id', string='Service Lines')
    part_line_ids = fields.One2many('repair.issue.template.part', 'template_id', string='Part Lines')


class RepairIssueTemplateService(models.Model):
    _name = 'repair.issue.template.service'
    _description = 'Repair Issue Template Service'
    _order = 'sequence, id'

    template_id = fields.Many2one('repair.issue.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    service_id = fields.Many2one('repair.service', string='Service', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    price = fields.Float(string='Price')


class RepairIssueTemplatePart(models.Model):
    _name = 'repair.issue.template.part'
    _description = 'Repair Issue Template Part'
    _order = 'sequence, id'

    template_id = fields.Many2one('repair.issue.template', string='Template', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
