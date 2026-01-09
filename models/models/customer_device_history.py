from odoo import models, fields, api, tools


class CustomerDeviceHistory(models.Model):
    _name = 'customer.device.history'
    _description = 'Customer Device Repair History'
    _auto = False
    _rec_name = 'customer_id'

    customer_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    brand_id = fields.Many2one('repair.brand', string='Brand', readonly=True)
    model_id = fields.Many2one('repair.model', string='Model', readonly=True)
    job_count = fields.Integer(string='Repairs', readonly=True)
    repeat_issue_jobs = fields.Integer(string='Repeat Issue Jobs', readonly=True)
    unique_issues = fields.Integer(string='Unique Issues', readonly=True)
    total_spend = fields.Monetary(string='Cumulative Spend', readonly=True, currency_field='currency_id')
    last_repair_date = fields.Datetime(string='Last Repair Date', readonly=True)
    currency_id = fields.Many2one('res.currency', related='customer_id.company_id.currency_id', readonly=True)

    def _select(self):
        return """
            WITH base AS (
                SELECT
                    jc.id,
                    jc.customer_id,
                    jc.brand_id,
                    jc.model_id,
                    jc.problem_description,
                    jc.total_amount,
                    jc.completion_date,
                    jc.create_date
                FROM job_card jc
                WHERE jc.customer_id IS NOT NULL
            ), issue_cte AS (
                SELECT
                    b.*,
                    COUNT(*) OVER (PARTITION BY b.customer_id, b.model_id, b.problem_description) AS issue_ct
                FROM base b
            )
            SELECT
                ROW_NUMBER() OVER() AS id,
                customer_id,
                brand_id,
                model_id,
                COUNT(*) AS job_count,
                SUM(CASE WHEN issue_ct > 1 THEN 1 ELSE 0 END) AS repeat_issue_jobs,
                COUNT(DISTINCT problem_description) AS unique_issues,
                SUM(COALESCE(total_amount, 0)) AS total_spend,
                MAX(COALESCE(completion_date, create_date)) AS last_repair_date
            FROM issue_cte
            GROUP BY customer_id, brand_id, model_id
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"CREATE OR REPLACE VIEW {self._table} AS ({self._select()})")
