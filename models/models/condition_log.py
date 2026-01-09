from odoo import models, fields


class RepairConditionLog(models.Model):
    _name = 'repair.condition.log'
    _description = 'Repair Part Condition Change Log'
    _order = 'create_date desc'

    job_card_id = fields.Many2one('job.card', string='Job Card', index=True, ondelete='cascade')
    part_line_id = fields.Many2one('job.card.part.line', string='Part Line', index=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='Changed By', default=lambda self: self.env.user)
    before_status = fields.Selection([('good', 'Good'), ('condemned', 'Condemned')], string='Before Status')
    after_status = fields.Selection([('good', 'Good'), ('condemned', 'Condemned')], string='After Status')
    before_scope = fields.Selection([('customer', 'Customer'), ('warehouse', 'Warehouse')], string='Before Scope')
    after_scope = fields.Selection([('customer', 'Customer'), ('warehouse', 'Warehouse')], string='After Scope')
    before_reason = fields.Text(string='Before Reason')
    after_reason = fields.Text(string='After Reason')
    before_date = fields.Date(string='Before Date')
    after_date = fields.Date(string='After Date')
    before_qty = fields.Float(string='Before Quantity')
    after_qty = fields.Float(string='After Quantity')
    create_date = fields.Datetime(string='Changed On', readonly=True)
