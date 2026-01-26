from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class JobCardServiceLine(models.Model):
    _name = 'job.card.service.line'
    _description = 'Job Card Service Line'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True, ondelete='cascade')
    service_id = fields.Many2one('repair.service', string='Service', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price', required=True)
    quantity = fields.Float(string='Quantity', default=1)
    price_total = fields.Float(string='Total', compute='_compute_total', store=True)
    
    @api.depends('price', 'quantity')
    def _compute_total(self):
        for line in self:
            line.price_total = line.price * line.quantity

    @api.onchange('service_id', 'job_card_id')
    def _onchange_service_id_set_price(self):
        for line in self:
            if not line.service_id:
                continue
            if not line.description:
                line.description = line.service_id.description or line.service_id.name
            if line.job_card_id and line.job_card_id.warranty:
                line.price = 0.0
            else:
                line.price = line.service_id.price

class JobCardPartLine(models.Model):
    _name = 'job.card.part.line'
    _description = 'Job Card Part Line'
    
    job_card_id = fields.Many2one('job.card', string='Job Card', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', required=True, default=1)
    unit_price = fields.Float(string='Unit Price', required=True)
    price_total = fields.Float(string='Total', compute='_compute_total', store=True)
    stock_available = fields.Float(string='Available Stock', related='product_id.qty_available')
    condition_status = fields.Selection([
        ('good', 'Good'),
        ('condemned', 'Condemned'),
    ], string='Condition', default='good', required=True)
    condemned_scope = fields.Selection([
        ('customer', 'Customer'),
        ('warehouse', 'Warehouse'),
    ], string='Condemned For', default=lambda self: self.env.context.get('default_condemned_scope'))
    condition_reason = fields.Text(string='Condition Reason')
    condition_date = fields.Date(string='Condition Date')
    condemned_move_id = fields.Many2one('stock.move', string='Non-usable Move', readonly=True, copy=False)

    def _infer_condemned_scope(self, vals=None):
        """Best-effort inference when editable one2many doesn't pass readonly fields/defaults."""
        ctx = self.env.context
        for key in ('default_condemned_scope', 'condemned_scope'):
            if ctx.get(key):
                return ctx.get(key)

        params = ctx.get('params') or {}
        view_id = ctx.get('view_id') or params.get('view_id')
        if view_id:
            view = self.env['ir.ui.view'].browse(view_id)
            xml_id = getattr(view, 'xml_id', False)
            if xml_id == 'mobile_repair_management.view_job_card_part_line_condemned_customer_inline_tree':
                return 'customer'
            if xml_id == 'mobile_repair_management.view_job_card_part_line_condemned_inline_tree':
                return 'warehouse'
        return False
    
    @api.depends('unit_price', 'quantity')
    def _compute_total(self):
        for line in self:
            line.price_total = line.unit_price * line.quantity

    @api.onchange('product_id', 'job_card_id')
    def _onchange_product_id_set_price(self):
        for line in self:
            if not line.product_id:
                continue
            if not line.description:
                line.description = line.product_id.display_name
            if line.job_card_id and line.job_card_id.warranty:
                line.unit_price = 0.0
            else:
                line.unit_price = line.product_id.list_price

    @api.onchange('condition_status')
    def _onchange_condition_status_set_scope(self):
        for line in self:
            if line.condition_status != 'condemned':
                # Keep it clean for normal parts
                line.condemned_scope = False
                return
            if not line.condemned_scope:
                inferred = line._infer_condemned_scope()
                line.condemned_scope = inferred or 'customer'

    @api.constrains('condition_status', 'condition_reason', 'condemned_scope')
    def _check_condition_reason(self):
        for line in self:
            if line.condition_status == 'condemned' and not line.condition_reason:
                raise ValidationError(_('Please provide a reason for condemned parts.'))
            if line.condition_status == 'condemned' and not line.condemned_scope:
                raise ValidationError(_('Specify whether the condemned part is for the customer or warehouse.'))

    def _get_source_location(self):
        self.ensure_one()
        company = self.job_card_id.company_id or self.env.company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)
        if not warehouse or not warehouse.lot_stock_id:
            raise UserError(_('No warehouse with a stock location is configured for company %s.') % company.name)
        return warehouse.lot_stock_id

    def _get_condemned_location(self):
        self.ensure_one()
        company = self.job_card_id.company_id or self.env.company
        location = self.env['stock.location'].search([
            ('scrap_location', '=', True),
            ('company_id', 'in', [False, company.id]),
        ], limit=1)
        if not location:
            location = self.env.ref('stock.stock_location_scrapped', raise_if_not_found=False)
            if location and location.company_id and location.company_id != company:
                location = False
        if not location:
            raise UserError(_('Configure a non-usable (scrap/condemned) location for company %s.') % company.name)
        return location

    def _create_condemned_move(self):
        for line in self:
            if line.condition_status != 'condemned':
                continue
            if line.condemned_scope != 'warehouse':
                continue
            if line.condemned_move_id or line.quantity <= 0:
                continue

            source_location = line._get_source_location()
            condemned_location = line._get_condemned_location()

            move = self.env['stock.move'].create({
                'name': _('Condemned part for %s') % (line.job_card_id.name or ''),
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': condemned_location.id,
                'company_id': (line.job_card_id.company_id or self.env.company).id,
                'origin': line.job_card_id.name,
                'job_card_id': line.job_card_id.id,
                'job_card_part_line_id': line.id,
            })
            move._action_confirm()
            move_line_vals = move._prepare_move_line_vals(quantity=line.quantity)
            self.env['stock.move.line'].create(move_line_vals)
            move._action_done()
            line.condemned_move_id = move.id

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(v) for v in vals_list]

        default_status = self.env.context.get('default_condition_status')
        for vals in vals_list:
            if default_status and not vals.get('condition_status'):
                vals['condition_status'] = default_status

            if vals.get('condition_status') == 'condemned' and not vals.get('condemned_scope'):
                inferred = self._infer_condemned_scope(vals)
                vals['condemned_scope'] = inferred or 'customer'

            if vals.get('job_card_id') and not vals.get('unit_price') and vals.get('product_id'):
                job = self.env['job.card'].browse(vals['job_card_id'])
                vals['unit_price'] = 0.0 if job.warranty else self.env['product.product'].browse(vals['product_id']).list_price

            if vals.get('condition_status') == 'condemned' and not vals.get('condition_date'):
                vals['condition_date'] = fields.Date.context_today(self)

        records = super().create(vals_list)
        records._create_condemned_move()
        return records

    def write(self, vals):
        vals = dict(vals)
        status_in_vals = vals.get('condition_status')
        if status_in_vals == 'condemned' and not vals.get('condition_date'):
            vals['condition_date'] = fields.Date.context_today(self)

        default_status = self.env.context.get('default_condition_status')
        if default_status and 'condition_status' not in vals:
            vals['condition_status'] = default_status

        # Lock scope based on tab context (customer/warehouse) when condemned.
        if vals.get('condition_status') == 'condemned' or any(r.condition_status == 'condemned' for r in self):
            if 'condemned_scope' not in vals:
                inferred = self._infer_condemned_scope(vals)
                vals['condemned_scope'] = inferred or 'customer'

        if vals.get('product_id') and not vals.get('unit_price'):
            job = self.job_card_id
            vals.setdefault('unit_price', 0.0 if (job and job.warranty) else self.env['product.product'].browse(vals['product_id']).list_price)

        res = super().write(vals)

        condemned_lines = self.filtered(lambda l: l.condition_status == 'condemned' and not l.condemned_move_id)
        if condemned_lines:
            condemned_lines._create_condemned_move()
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    job_card_id = fields.Many2one('job.card', string='Job Card', readonly=True)
    job_card_part_line_id = fields.Many2one('job.card.part.line', string='Job Card Part Line', readonly=True)