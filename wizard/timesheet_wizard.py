from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TimesheetWizard(models.TransientModel):
    _name = 'timesheet.wizard'
    _description = 'Timesheet Entry Wizard'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True)
    user_id = fields.Many2one('res.users', string='Technician', required=True, default=lambda self: self.env.user)
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    duration = fields.Float(string='Duration (hours)', required=True)
    description = fields.Text(string='Work Done', required=True)
    is_billable = fields.Boolean(string='Billable', default=True)
    
    def action_save_timesheet(self):
        if self.duration <= 0:
            raise UserError(_('Duration must be greater than 0!'))
        
        self.env['repair.timesheet'].create({
            'job_card_id': self.job_card_id.id,
            'user_id': self.user_id.id,
            'date': self.date,
            'duration': self.duration,
            'description': self.description,
            'is_billable': self.is_billable,
        })
        
        return {'type': 'ir.actions.act_window_close'}