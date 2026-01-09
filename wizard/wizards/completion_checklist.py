from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CompletionChecklistWizard(models.TransientModel):
    _name = 'completion.checklist.wizard'
    _description = 'Completion Checklist'

    job_card_id = fields.Many2one('job.card', string='Job Card', required=True)
    tests_passed = fields.Boolean(string='Functional Tests Passed', required=True)
    customer_acknowledged = fields.Boolean(string='Customer Acknowledged Issues/Condition', required=True)
    notes = fields.Text(string='Notes')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            defaults['job_card_id'] = active_id
        return defaults

    def action_confirm(self):
        self.ensure_one()
        job_card = self.job_card_id
        if job_card.state != 'in_progress':
            raise UserError(_('Only In Progress repairs can be completed.'))
        if not self.tests_passed:
            raise UserError(_('Functional tests must be passed before completing the repair.'))
        if not self.customer_acknowledged:
            raise UserError(_('Customer acknowledgment is required before completion.'))

        job_card.write({
            'completion_checklist_done': True,
            'completion_tests_passed': self.tests_passed,
            'completion_customer_acknowledged': self.customer_acknowledged,
            'completion_checklist_notes': self.notes,
            'completion_checklist_user_id': self.env.user.id,
            'completion_checklist_date': fields.Datetime.now(),
        })
        return job_card.action_complete_repair()
