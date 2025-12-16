from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AssignTeamWizard(models.TransientModel):
    _name = 'job.card.assign.team.wizard'
    _description = 'Assign Repair Team Wizard'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True)
    team_id = fields.Many2one('repair.team', string='Repair Team', required=True)
    assigned_member_ids = fields.Many2many('res.users', string='Assigned Members')
    expected_duration = fields.Float(string='Expected Duration (hours)', required=True)
    start_date = fields.Datetime(string='Start Date', default=fields.Datetime.now)
    
    @api.onchange('team_id')
    def _onchange_team_id(self):
        if self.team_id:
            self.assigned_member_ids = self.team_id.member_ids
    
    def action_assign_team(self):
        for wizard in self:
            if not wizard.assigned_member_ids:
                raise UserError(_('Please assign at least one team member!'))
            
            wizard.job_card_id.write({
                'team_id': wizard.team_id.id,
                'assigned_member_ids': [(6, 0, wizard.assigned_member_ids.ids)],
                'expected_duration': wizard.expected_duration,
                'start_date': wizard.start_date,
            })
            
            # Create task in project
            task_vals = {
                'name': f'Repair - {wizard.job_card_id.name}',
                'project_id': wizard.team_id.project_id.id if wizard.team_id.project_id else False,
                'user_ids': [(6, 0, wizard.assigned_member_ids.ids)],
                'description': wizard.job_card_id.problem_description,
                'planned_hours': wizard.expected_duration,
                'date_deadline': wizard.start_date,
                'repair_team_id': wizard.team_id.id,
                'job_card_id': wizard.job_card_id.id,
            }
            
            task = self.env['project.task'].create(task_vals)
            wizard.job_card_id.task_id = task.id
            
            # Update job card state
            wizard.job_card_id.state = 'in_progress'
        
        return {'type': 'ir.actions.act_window_close'}