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
    needed_by_date = fields.Date(string='Needed By')
    picking_move_id = fields.Many2one('stock.move', string='Stock Move', readonly=True, copy=False)
    reserved_qty = fields.Float(string='Reserved Qty', compute='_compute_reservation', store=False)
    reservation_status = fields.Selection([
        ('none', 'Not Requested'),
        ('waiting', 'Waiting'),
        ('partially_reserved', 'Partially Reserved'),
        ('reserved', 'Reserved'),
        ('done', 'Done'),
    ], string='Reservation Status', compute='_compute_reservation', store=False)
    condition_status = fields.Selection([
        ('good', 'Good'),
        ('condemned', 'Condemned'),
    ], string='Condition', default='good', required=True)
    condemned_scope = fields.Selection([
        ('customer', 'Customer'),
        ('warehouse', 'Warehouse'),
    ], string='Condemned For')
    condition_reason = fields.Text(string='Condition Reason')
    condition_date = fields.Date(string='Condition Date')
    condemned_move_id = fields.Many2one('stock.move', string='Non-usable Move', readonly=True, copy=False)
    condemned_unit_cost = fields.Float(string='Condemned Unit Cost', readonly=True, copy=False)
    condemned_total_cost = fields.Float(string='Condemned Total Cost', readonly=True, copy=False)
    condemned_currency_id = fields.Many2one('res.currency', string='Currency', related='job_card_id.currency_id', store=True, readonly=True)
    condition_changelog_ids = fields.One2many('repair.condition.log', 'part_line_id', string='Condition Log', readonly=True)
    
    @api.depends('unit_price', 'quantity')
    def _compute_total(self):
        for line in self:
            line.price_total = line.unit_price * line.quantity

    @api.constrains('condition_status', 'condition_reason', 'condemned_scope')
    def _check_condition_reason(self):
        for line in self:
            if line.condition_status == 'condemned' and not line.condition_reason:
                raise ValidationError(_('Please provide a reason for condemned parts.'))
            if line.condition_status == 'condemned' and not line.condemned_scope:
                raise ValidationError(_('Specify whether the condemned part is for the customer or warehouse.'))

    @api.depends('picking_move_id.state', 'picking_move_id.reserved_availability', 'picking_move_id.product_uom_qty')
    def _compute_reservation(self):
        for line in self:
            move = line.picking_move_id
            if not move:
                line.reserved_qty = 0.0
                line.reservation_status = 'none'
                continue
            line.reserved_qty = move.reserved_availability
            if move.state == 'done':
                line.reservation_status = 'done'
            elif move.reserved_availability >= move.product_uom_qty:
                line.reservation_status = 'reserved'
            elif move.reserved_availability > 0:
                line.reservation_status = 'partially_reserved'
            else:
                line.reservation_status = 'waiting'

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
            cost_value = abs(move.value) if move.value else line.product_id.standard_price * line.quantity
            line.condemned_total_cost = cost_value
            line.condemned_unit_cost = (cost_value / line.quantity) if line.quantity else 0.0

    @api.model
    def create(self, vals):
        vals = dict(vals)
        if vals.get('condition_status') == 'condemned' and not vals.get('condition_date'):
            vals['condition_date'] = fields.Date.context_today(self)
        if not vals.get('needed_by_date') and vals.get('job_card_id'):
            job_card = self.env['job.card'].browse(vals['job_card_id'])
            vals['needed_by_date'] = job_card.parts_needed_date or (job_card.promised_date and fields.Date.to_date(job_card.promised_date)) or fields.Date.context_today(self)
        record = super().create(vals)
        record._create_condemned_move()
        return record

    def write(self, vals):
        vals = dict(vals)
        status_in_vals = vals.get('condition_status')
        if status_in_vals == 'condemned' and not vals.get('condition_date'):
            vals['condition_date'] = fields.Date.context_today(self)

        # Capture before values for audit log
        tracked_fields = ['condition_status', 'condemned_scope', 'condition_reason', 'condition_date', 'quantity']
        before = {f: getattr(self, f) for f in tracked_fields}

        res = super().write(vals)

        # Log changes
        for line in self:
            after = {f: getattr(line, f) for f in tracked_fields}
            if any(before[f] != after[f] for f in tracked_fields):
                line._log_condition_change(before, after)

        condemned_lines = self.filtered(lambda l: l.condition_status == 'condemned' and not l.condemned_move_id)
        if condemned_lines:
            condemned_lines._create_condemned_move()
        return res

    def _log_condition_change(self, before, after):
        self.ensure_one()
        self.env['repair.condition.log'].create({
            'part_line_id': self.id,
            'job_card_id': self.job_card_id.id,
            'user_id': self.env.uid,
            'before_status': before.get('condition_status'),
            'after_status': after.get('condition_status'),
            'before_scope': before.get('condemned_scope'),
            'after_scope': after.get('condemned_scope'),
            'before_reason': before.get('condition_reason'),
            'after_reason': after.get('condition_reason'),
            'before_date': before.get('condition_date'),
            'after_date': after.get('condition_date'),
            'before_qty': before.get('quantity'),
            'after_qty': after.get('quantity'),
        })


class StockMove(models.Model):
    _inherit = 'stock.move'

    job_card_id = fields.Many2one('job.card', string='Job Card', readonly=True)
    job_card_part_line_id = fields.Many2one('job.card.part.line', string='Job Card Part Line', readonly=True)