from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class JobCard(models.Model):
    _name = 'job.card'
    _description = 'Repair Job Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Sequence
    name = fields.Char(string='Job Card Number', default=lambda self: _('New'), readonly=True, copy=False)
    
    # States
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('quotation', 'Quotation'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    
    # Customer
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    customer_phone = fields.Char(string='Customer Phone', related='customer_id.phone', store=True)
    customer_email = fields.Char(string='Customer Email', related='customer_id.email', store=True)
    
    # Device
    brand_id = fields.Many2one('repair.brand', string='Brand', required=True)
    series_id = fields.Many2one('repair.series', string='Series', required=True)
    model_id = fields.Many2one('repair.model', string='Model', required=True)
    imei = fields.Char(string='IMEI Number')
    serial_number = fields.Char(string='Serial Number')
    device_condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('broken', 'Broken'),
    ], string='Device Condition', default='good')
    device_accessories = fields.Text(string='Device Accessories')
    problem_description = fields.Text(string='Problem Description', required=True)
    issue_template_id = fields.Many2one('repair.issue.template', string='Predefined Issue')
    device_photo = fields.Image(string='Device Photo')
    damage_photo = fields.Image(string='Damage Photo')
    
    # Warranty
    warranty = fields.Boolean(string='Under Warranty', default=False)
    warranty_number = fields.Char(string='Warranty Number')
    warranty_expiry_date = fields.Date(string='Warranty Expiry Date')
    
    # Inspection
    inspection_date = fields.Datetime(string='Inspection Date', default=fields.Datetime.now)
    inspection_type = fields.Selection([
        ('basic', 'Basic Inspection'),
        ('detailed', 'Detailed Inspection'),
        ('technical', 'Technical Inspection'),
    ], string='Inspection Type', default='basic')
    delivery_type = fields.Selection([
        ('pickup', 'Customer Pickup'),
        ('delivery', 'Home Delivery'),
        ('courier', 'Courier Service'),
    ], string='Delivery Type', default='pickup')
    
    # Services and Parts
    service_ids = fields.One2many('job.card.service.line', 'job_card_id', string='Services')
    part_ids = fields.One2many('job.card.part.line', 'job_card_id', string='Parts')
    
    # Totals
    service_total = fields.Float(string='Service Total', compute='_compute_totals', store=True)
    part_total = fields.Float(string='Parts Total', compute='_compute_totals', store=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_totals', store=True)
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_totals', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_totals', store=True)
    condemned_total_cost = fields.Monetary(string='Condemned Cost', compute='_compute_condemned_cost', currency_field='currency_id', store=True)
    
    # Quotation
    quotation_date = fields.Datetime(string='Quotation Date')
    quotation_valid_until = fields.Date(string='Quotation Valid Until')
    is_quotation_sent = fields.Boolean(string='Quotation Sent')
    customer_approval = fields.Selection([
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Customer Approval', default='pending')
    approval_date = fields.Datetime(string='Approval Date')
    
    # Team
    team_id = fields.Many2one('repair.team', string='Repair Team')
    assigned_member_ids = fields.Many2many('res.users', string='Assigned Members')
    expected_duration = fields.Float(string='Expected Duration (hours)')
    start_date = fields.Datetime(string='Start Date')
    completion_date = fields.Datetime(string='Completion Date')
    promised_date = fields.Datetime(string='Promised Date')
    sla_status = fields.Selection([
        ('pending', 'Pending'),
        ('on_time', 'On Time'),
        ('late', 'Late'),
    ], string='SLA Status', compute='_compute_sla', store=True)
    sla_delay_hours = fields.Float(string='SLA Delay (hours)', compute='_compute_sla', store=True)
    is_rework = fields.Boolean(string='Rework Job', default=False)
    
    # Stock
    picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    parts_needed_date = fields.Date(string='Parts Needed By')
    parts_request_status = fields.Selection([
        ('none', 'Not Requested'),
        ('requested', 'Requested'),
        ('partially_reserved', 'Partially Reserved'),
        ('reserved', 'Reserved'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Parts Reservation', compute='_compute_parts_request_status', store=False)
    
    # Invoice
    invoice_id = fields.Many2one('account.move', string='Invoice')
    invoice_status = fields.Selection([
        ('no', 'Nothing to Invoice'),
        ('to_invoice', 'To Invoice'),
        ('invoiced', 'Fully Invoiced'),
    ], string='Invoice Status', default='no', compute='_compute_invoice_status', store=True)
    payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ], string='Payment Status', compute='_compute_payment_status')
    
    # Task
    task_id = fields.Many2one('project.task', string='Repair Task')
    
    # Timesheets
    timesheet_ids = fields.One2many('repair.timesheet', 'job_card_id', string='Timesheets')

    # Completion Checklist
    completion_checklist_done = fields.Boolean(string='Checklist Completed', default=False, tracking=True)
    completion_tests_passed = fields.Boolean(string='Completion Tests Passed', readonly=True)
    completion_customer_acknowledged = fields.Boolean(string='Customer Acknowledged', readonly=True)
    completion_checklist_notes = fields.Text(string='Completion Notes', readonly=True)
    completion_checklist_user_id = fields.Many2one('res.users', string='Checklist Completed By', readonly=True)
    completion_checklist_date = fields.Datetime(string='Checklist Completed On', readonly=True)
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    
    # Dates
    create_date = fields.Datetime(string='Creation Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated', readonly=True)
    
    # Computed Fields
    @api.depends('service_ids.price_total', 'part_ids.price_total', 'part_ids.condition_status')
    def _compute_totals(self):
        for record in self:
            service_total = sum(record.service_ids.mapped('price_total'))
            part_total = sum(record.part_ids.filtered(lambda l: l.condition_status != 'condemned').mapped('price_total'))
            record.service_total = service_total
            record.part_total = part_total
            record.subtotal = service_total + part_total
            # Tax computation not specified; keep zero placeholder for now.
            record.tax_amount = 0.0
            record.total_amount = record.subtotal + record.tax_amount

    @api.depends('part_ids.condemned_total_cost')
    def _compute_condemned_cost(self):
        for record in self:
            record.condemned_total_cost = sum(record.part_ids.mapped('condemned_total_cost'))

    @api.depends('promised_date', 'completion_date', 'state')
    def _compute_sla(self):
        for record in self:
            status = 'pending'
            delay = 0.0
            if record.promised_date:
                reference_date = record.completion_date or fields.Datetime.now()
                if record.state == 'completed' and record.completion_date:
                    status = 'on_time' if record.completion_date <= record.promised_date else 'late'
                else:
                    status = 'pending' if reference_date <= record.promised_date else 'late'
                if reference_date and reference_date > record.promised_date:
                    delay = (reference_date - record.promised_date).total_seconds() / 3600.0
            record.sla_status = status
            record.sla_delay_hours = delay

    @api.depends('picking_id.state', 'picking_id.move_ids_without_package.reserved_availability', 'picking_id.move_ids_without_package.product_uom_qty')
    def _compute_parts_request_status(self):
        for record in self:
            picking = record.picking_id
            status = 'none'
            if picking:
                if picking.state == 'done':
                    status = 'done'
                elif picking.state == 'cancel':
                    status = 'cancelled'
                else:
                    required_qty = sum(picking.move_ids_without_package.mapped('product_uom_qty'))
                    reserved_qty = sum(picking.move_ids_without_package.mapped('reserved_availability'))
                    if required_qty:
                        if reserved_qty >= required_qty:
                            status = 'reserved'
                        elif reserved_qty > 0:
                            status = 'partially_reserved'
                        else:
                            status = 'requested'
                    else:
                        status = 'requested'
            record.parts_request_status = status
    
    # CRUD
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('job.card') or _('New')
        return super().create(vals)
    
    # Business Methods
    def action_mark_requested(self):
        self.write({'state': 'requested'})
    
    def action_generate_quotation(self):
        if self.warranty:
            raise UserError(_('Cannot generate quotation for warranty repairs!'))
        
        self.write({
            'state': 'quotation',
            'quotation_date': fields.Datetime.now(),
            'quotation_valid_until': fields.Date.today() + timedelta(days=7),
            'is_quotation_sent': True,
        })
        try:
            report_action = self.env.ref('mobile_repair_management.action_job_card_report_template')
        except ValueError:
            report_action = self.env['ir.actions.report']._get_report_from_name('mobile_repair_management.report_job_card_quotation')
            if not report_action:
                raise UserError(_('Quotation report definition is missing. Please upgrade the module.'))
        return report_action.report_action(self)

    @api.onchange('issue_template_id')
    def _onchange_issue_template(self):
        for record in self:
            template = record.issue_template_id
            if not template:
                continue
            service_commands = []
            part_commands = []
            for line in template.service_line_ids:
                service_commands.append((0, 0, {
                    'service_id': line.service_id.id,
                    'description': line.description or line.service_id.name,
                    'price': line.price,
                    'quantity': line.quantity,
                }))
            for line in template.part_line_ids:
                part_commands.append((0, 0, {
                    'product_id': line.product_id.id,
                    'description': line.description or line.product_id.display_name,
                    'unit_price': line.unit_price,
                    'quantity': line.quantity,
                    'condition_status': 'good',
                }))
            record.service_ids = [(5, 0, 0)] + service_commands if service_commands else [(5, 0, 0)]
            record.part_ids = [(5, 0, 0)] + part_commands if part_commands else [(5, 0, 0)]
    
    def action_customer_approve(self):
        self.write({
            'state': 'approved',
            'customer_approval': 'approved',
            'approval_date': fields.Datetime.now(),
        })
        for record in self:
            # Auto-request parts upon approval to reserve stock
            record._ensure_parts_picking()
    
    def action_customer_reject(self):
        self.write({
            'state': 'rejected',
            'customer_approval': 'rejected',
        })
    
    def action_assign_team(self):
        for record in self:
            if not record.warranty and not record.invoice_id:
                raise UserError(_('Create the invoice before assigning a team for non-warranty repairs.'))
        return {
            'name': _('Assign Repair Team'),
            'type': 'ir.actions.act_window',
            'res_model': 'assign.team.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_job_card_id': self.id},
        }
    
    def action_start_repair(self):
        for record in self:
            if record.state in ['in_progress', 'completed', 'rejected']:
                raise UserError(_('Repair is already started or closed.'))
            if not record.team_id:
                raise UserError(_('Assign a repair team before starting.'))
            if not record.warranty:
                if not record.invoice_id:
                    raise UserError(_('Create the invoice before starting a non-warranty repair.'))
                if record.invoice_id.payment_state != 'paid':
                    raise UserError(_('Register payment before starting a non-warranty repair.'))
        task_vals = {
            'name': f'Repair - {self.name}',
            'project_id': self.team_id.project_id.id if self.team_id else False,
            'user_ids': [(6, 0, self.assigned_member_ids.ids)],
            'description': self.problem_description,
        }
        
        task = self.env['project.task'].create(task_vals)
        
        self.write({
            'state': 'in_progress',
            'task_id': task.id,
            'start_date': fields.Datetime.now(),
        })
    
    def action_complete_repair(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError(_('You can only complete repairs that are In Progress.'))
            if not rec.completion_checklist_done:
                raise UserError(_('Finish the completion checklist before marking this repair complete.'))
        self.write({
            'state': 'completed',
            'completion_date': fields.Datetime.now(),
        })

    def action_cancel_repair(self):
        for record in self:
            if record.state == 'completed':
                raise UserError(_('Cannot cancel a completed repair.'))
        self.write({'state': 'rejected'})

    def action_open_completion_checklist(self):
        self.ensure_one()
        if self.state != 'in_progress':
            raise UserError(_('You can only complete repairs that are In Progress.'))
        view = self.env.ref('mobile_repair_management.view_completion_checklist_wizard')
        return {
            'name': _('Completion Checklist'),
            'type': 'ir.actions.act_window',
            'res_model': 'completion.checklist.wizard',
            'view_mode': 'form',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {
                'default_job_card_id': self.id,
                'active_id': self.id,
                'active_model': 'job.card',
            },
        }
    
    def action_create_invoice(self):
        if self.warranty:
            raise UserError(_('Cannot create invoice for warranty repairs!'))
        
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_origin': self.name,
            'company_id': self.env.company.id,
            'invoice_line_ids': [],
        }
        
        # Add service lines
        for service in self.service_ids:
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'product_id': service.service_id.product_id.id if service.service_id.product_id else False,
                'name': service.service_id.name,
                'quantity': service.quantity,
                'price_unit': service.price,
                'account_id': self.env['account.account'].search([('code', '=', '400000')], limit=1).id,
            }))
        
        # Add part lines
        for part in self.part_ids.filtered(lambda p: p.condition_status != 'condemned'):
            invoice_vals['invoice_line_ids'].append((0, 0, {
                'product_id': part.product_id.id,
                'name': part.product_id.name,
                'quantity': part.quantity,
                'price_unit': part.unit_price,
                'account_id': part.product_id.property_account_income_id.id or part.product_id.categ_id.property_account_income_categ_id.id,
            }))
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }

    def _get_parts_needed_date(self):
        self.ensure_one()
        if self.parts_needed_date:
            return self.parts_needed_date
        if self.promised_date:
            return fields.Date.to_date(self.promised_date)
        return fields.Date.context_today(self)

    def _get_internal_picking_type(self):
        company = self.company_id or self.env.company
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            '|', ('warehouse_id.company_id', '=', company.id), ('warehouse_id', '=', False),
        ], limit=1)
        if not picking_type:
            raise UserError(_('No internal transfer picking type configured for company %s.') % company.name)
        return picking_type

    def action_request_parts(self):
        self.ensure_one()
        self._ensure_parts_picking()
        if not self.picking_id:
            raise UserError(_('No parts to request for this job card.'))
        return self.action_view_picking()

    def _ensure_parts_picking(self):
        self.ensure_one()
        part_lines = self.part_ids.filtered(lambda p: p.condition_status != 'condemned' and p.quantity > 0 and p.product_id and p.product_id.type in ['product', 'consu'])
        if not part_lines:
            return False

        picking_type = self._get_internal_picking_type()
        warehouse = picking_type.warehouse_id or self.env['stock.warehouse'].search([
            ('company_id', '=', (self.company_id or self.env.company).id)
        ], limit=1)
        source_location = picking_type.default_location_src_id or (warehouse.lot_stock_id if warehouse else False)
        dest_location = picking_type.default_location_dest_id or (warehouse.lot_stock_id if warehouse else False)

        if not source_location or not dest_location:
            raise UserError(_('Configure source/destination locations on the internal picking type for %s.') % ((self.company_id or self.env.company).name))

        needed_date = self._get_parts_needed_date()
        picking_dates = []

        picking = self.picking_id if self.picking_id and self.picking_id.state not in ['done', 'cancel'] else False

        if not picking:
            picking_vals = {
                'picking_type_id': picking_type.id,
                'origin': self.name,
                'partner_id': self.customer_id.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
                'scheduled_date': needed_date,
                'company_id': (self.company_id or self.env.company).id,
            }
            picking = self.env['stock.picking'].create(picking_vals)
        else:
            # Refresh moves to match current parts list
            self.part_ids.write({'picking_move_id': False})
            picking.move_ids_without_package.filtered(lambda m: m.state not in ['done', 'cancel']).unlink()

        for part in part_lines:
            line_needed_date = part.needed_by_date or needed_date
            picking_dates.append(line_needed_date)
            move_vals = {
                'name': _('Job %s - %s') % (self.name, part.product_id.display_name),
                'product_id': part.product_id.id,
                'product_uom_qty': part.quantity,
                'product_uom': part.product_id.uom_id.id,
                'location_id': source_location.id,
                'location_dest_id': dest_location.id,
                'company_id': (self.company_id or self.env.company).id,
                'picking_id': picking.id,
                'origin': self.name,
                'job_card_id': self.id,
                'job_card_part_line_id': part.id,
                'date': line_needed_date,
                'scheduled_date': line_needed_date,
            }
            move = self.env['stock.move'].create(move_vals)
            part.picking_move_id = move.id
            part.needed_by_date = line_needed_date

        picking.action_confirm()
        picking.action_assign()

        if picking_dates:
            picking.scheduled_date = min(picking_dates)

        self.picking_id = picking.id
        return picking
    
    def action_register_payment(self):
        if not self.invoice_id:
            raise UserError(_('No invoice found!'))
        
        return {
            'name': _('Register Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.invoice_id.ids,
            },
        }
    
    def action_view_picking(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError(_('No picking created for this job card yet.'))
        return {
            'name': _('Stock Picking'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
            'view_mode': 'form',
        }
    
    def action_view_invoice(self):
        return {
            'name': _('Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
        }
    
    def action_view_task(self):
        return {
            'name': _('Repair Task'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': self.task_id.id,
            'view_mode': 'form',
        }