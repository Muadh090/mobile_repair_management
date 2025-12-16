from odoo import models, fields, api

class JobCardReport(models.AbstractModel):
    _name = 'report.mobile_repair_management.job_card_report_template'
    _description = 'Job Card Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['job.card'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'job.card',
            'docs': docs,
            'data': data,
        }