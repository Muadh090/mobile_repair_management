from odoo import models, fields, api, tools


class TechnicianPerformance(models.Model):
    _name = 'technician.performance'
    _description = 'Technician Performance KPIs'
    _auto = False
    _rec_name = 'technician_id'

    technician_id = fields.Many2one('res.users', string='Technician', readonly=True)
    jobs_completed = fields.Integer(string='Jobs Completed', readonly=True)
    sla_hits = fields.Integer(string='SLA Hits', readonly=True)
    sla_total = fields.Integer(string='SLA Total', readonly=True)
    sla_hit_rate = fields.Float(string='SLA Hit %', compute='_compute_sla_hit_rate')
    rework_count = fields.Integer(string='Reworks', readonly=True)
    parts_qty = fields.Float(string='Parts Qty', readonly=True)
    parts_value = fields.Monetary(string='Parts Value', readonly=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', related='technician_id.company_id.currency_id', readonly=True)

    @api.depends('sla_hits', 'sla_total')
    def _compute_sla_hit_rate(self):
        for record in self:
            if record.sla_total:
                record.sla_hit_rate = (record.sla_hits / record.sla_total) * 100.0
            else:
                record.sla_hit_rate = 0.0

    def _select(self):
        return """
            WITH tech_map AS (
                SELECT
                    jc.id AS job_card_id,
                    rel.res_users_id AS technician_id,
                    COALESCE(cnt.tech_count, 1) AS tech_count,
                    jc.state,
                    jc.sla_status,
                    jc.is_rework
                FROM job_card jc
                JOIN job_card_res_users_rel rel ON rel.job_card_id = jc.id
                LEFT JOIN (
                    SELECT job_card_id, COUNT(*) AS tech_count
                    FROM job_card_res_users_rel
                    GROUP BY job_card_id
                ) cnt ON cnt.job_card_id = jc.id
            )
            SELECT
                ROW_NUMBER() OVER() AS id,
                t.technician_id,
                SUM(CASE WHEN t.state = 'completed' THEN 1 ELSE 0 END) AS jobs_completed,
                SUM(CASE WHEN t.sla_status = 'on_time' THEN 1 ELSE 0 END) AS sla_hits,
                SUM(CASE WHEN t.sla_status IS NOT NULL THEN 1 ELSE 0 END) AS sla_total,
                SUM(CASE WHEN t.is_rework THEN 1 ELSE 0 END) AS rework_count,
                SUM(COALESCE(pl.quantity, 0) / NULLIF(t.tech_count, 0)) AS parts_qty,
                SUM(COALESCE(pl.price_total, 0) / NULLIF(t.tech_count, 0)) AS parts_value
            FROM tech_map t
            LEFT JOIN job_card_part_line pl ON pl.job_card_id = t.job_card_id AND pl.condition_status != 'condemned'
            GROUP BY t.technician_id
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"CREATE OR REPLACE VIEW {self._table} AS ({self._select()})")
