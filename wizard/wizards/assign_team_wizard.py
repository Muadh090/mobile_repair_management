from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AssignTeamWizard(models.TransientModel):
    _name = 'assign.team.wizard'
    _description = 'Assign Repair Team Wizard'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True)
    team_id = fields.Many2one('repair.team', string='Repair Team', required=True)
    assigned_member_ids = fields.Many2many('res.users', string='Assigned Members')
    expected_duration = fields.Float(string='Expected Duration (hours)', required=True)
    
    @api.onchange('team_id')
    def _onchange_team_id(self):
        if self.team_id:
            self.assigned_member_ids = self.team_id.member_ids
    
    def action_assign_team(self):
        if not self.assigned_member_ids:
            raise UserError(_('Please assign at least one team member!'))
        
        self.job_card_id.write({
            'team_id': self.team_id.id,
            'assigned_member_ids': [(6, 0, self.assigned_member_ids.ids)],
            'expected_duration': self.expected_duration,
        })
        
        return {'type': 'ir.actions.act_window_close'}