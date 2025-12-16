from odoo import models, fields, api
from datetime import datetime, timedelta

class RepairTeam(models.Model):
    _name = 'repair.team'
    _description = 'Repair Team'
    
    name = fields.Char(string='Team Name', required=True)
    manager_id = fields.Many2one('res.users', string='Team Manager', required=True)
    member_ids = fields.Many2many('res.users', 'repair_team_user_rel', 'team_id', 'user_id', string='Team Members')
    project_id = fields.Many2one('project.project', string='Associated Project')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string='Color', default=1)
    
    job_card_ids = fields.One2many('job.card', 'team_id', string='Job Cards')
    completed_jobs = fields.Integer(string='Completed Jobs', compute='_compute_completed_jobs', store=True)
    avg_repair_time = fields.Float(string='Average Repair Time (hours)', compute='_compute_avg_repair_time', store=True)
    
    @api.depends('job_card_ids.state')
    def _compute_completed_jobs(self):
        for team in self:
            team.completed_jobs = len(team.job_card_ids.filtered(lambda j: j.state == 'completed'))
    
    @api.depends('job_card_ids.completion_date', 'job_card_ids.start_date')
    def _compute_avg_repair_time(self):
        for team in self:
            completed = team.job_card_ids.filtered(lambda j: j.state == 'completed' and j.start_date and j.completion_date)
            if completed:
                total_hours = sum([
                    (j.completion_date - j.start_date).total_seconds() / 3600
                    for j in completed
                ])
                team.avg_repair_time = total_hours / len(completed)
            else:
                team.avg_repair_time = 0.0