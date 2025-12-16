from odoo import models, fields, api

class RepairTimesheetLine(models.Model):
    _name = 'repair.timesheet'
    _description = 'Repair Timesheet'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True)
    task_id = fields.Many2one('project.task', string='Task', related='job_card_id.task_id', store=True)
    user_id = fields.Many2one('res.users', string='Technician', required=True, default=lambda self: self.env.user)
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    duration = fields.Float(string='Duration (hours)', required=True)
    description = fields.Text(string='Work Done', required=True)
    is_billable = fields.Boolean(string='Billable', default=True)
    
    # Link to account.analytic.line
    analytic_line_id = fields.Many2one('account.analytic.line', string='Analytic Line')
    
    @api.model
    def create(self, vals):
        record = super(RepairTimesheetLine, self).create(vals)
        
        # Create analytic line if billable
        if record.is_billable and record.task_id:
            analytic_line_vals = {
                'name': record.description,
                'date': record.date,
                'unit_amount': record.duration,
                'employee_id': record.user_id.employee_id.id if record.user_id.employee_id else False,
                'account_id': record.task_id.project_id.analytic_account_id.id if record.task_id.project_id.analytic_account_id else False,
                'task_id': record.task_id.id,
                'project_id': record.task_id.project_id.id,
                'user_id': record.user_id.id,
            }
            
            analytic_line = self.env['account.analytic.line'].create(analytic_line_vals)
            record.analytic_line_id = analytic_line.id
        
        return record