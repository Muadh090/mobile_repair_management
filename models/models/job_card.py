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
        ('parts_requested', 'Parts Requested'),
        ('parts_arrived', 'Parts Arrived'),
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
    
    # Stock
    picking_id = fields.Many2one('stock.picking', string='Stock Picking')
    
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
    
    # Company
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    
    # Dates
    create_date = fields.Datetime(string='Creation Date', readonly=True)
    write_date = fields.Datetime(string='Last Updated', readonly=True)
    
    # Computed Fields
    @api.depends('service_ids.price_total', 'part_ids.price_total')
    def _compute_totals(self):
        for record in self:
            service_total = sum(record.service_ids.mapped('price_total'))
            part_total = sum(record.part_ids.mapped('price_total'))
            subtotal = service_total + part_total
            tax_amount = subtotal * 0.15  # 15% tax
            total_amount = subtotal + tax_amount
            
            record.service_total = service_total
            record.part_total = part_total
            record.subtotal = subtotal
            record.tax_amount = tax_amount
            record.total_amount = total_amount
    
    @api.depends('invoice_id')
    def _compute_invoice_status(self):
        for record in self:
            if record.invoice_id:
                record.invoice_status = 'invoiced'
            elif record.state == 'completed' and not record.warranty:
                record.invoice_status = 'to_invoice'
            else:
                record.invoice_status = 'no'
    
    @api.depends('invoice_id.payment_state')
    def _compute_payment_status(self):
        for record in self:
            if record.invoice_id:
                if record.invoice_id.payment_state == 'paid':
                    record.payment_status = 'paid'
                elif record.invoice_id.payment_state == 'partial':
                    record.payment_status = 'partially_paid'
                else:
                    record.payment_status = 'not_paid'
            else:
                record.payment_status = 'not_paid'
    
    # Constraints
    @api.constrains('warranty', 'warranty_expiry_date')
    def _check_warranty_expiry(self):
        for record in self:
            if record.warranty and record.warranty_expiry_date:
                if record.warranty_expiry_date < fields.Date.today():
                    raise ValidationError(_('Warranty has expired!'))
    
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
        return self.env.ref('mobile_repair_management.action_report_job_card_quotation').report_action(self)
    
    def action_customer_approve(self):
        self.write({
            'state': 'approved',
            'customer_approval': 'approved',
            'approval_date': fields.Datetime.now(),
        })
    
    def action_customer_reject(self):
        self.write({
            'state': 'rejected',
            'customer_approval': 'rejected',
        })
    
    def action_request_parts(self):
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']
        
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        
        picking_vals = {
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': self.team_id.project_id.location_id.id if self.team_id and self.team_id.project_id else picking_type.default_location_dest_id.id,
            'partner_id': self.customer_id.id,
            'scheduled_date': fields.Datetime.now(),
            'origin': self.name,
            'company_id': self.env.company.id,
        }
        
        picking = StockPicking.create(picking_vals)
        
        for part in self.part_ids:
            StockMove.create({
                'name': part.product_id.name,
                'product_id': part.product_id.id,
                'product_uom': part.product_id.uom_id.id,
                'product_uom_qty': part.quantity,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
                'company_id': self.env.company.id,
            })
        
        self.write({
            'state': 'parts_requested',
            'picking_id': picking.id,
        })
    
    def action_parts_arrived(self):
        if self.picking_id and self.picking_id.state == 'done':
            self.write({'state': 'parts_arrived'})
        else:
            raise UserError(_('Please validate the stock picking first!'))
    
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
            'planned_hours': self.expected_duration,
            'repair_team_id': self.team_id.id,
            'job_card_id': self.id,
        }
        
        task = self.env['project.task'].create(task_vals)
        
        self.write({
            'state': 'in_progress',
            'task_id': task.id,
            'start_date': fields.Datetime.now(),
        })
    
    def action_complete_repair(self):
        if any(rec.state != 'in_progress' for rec in self):
            raise UserError(_('You can only complete repairs that are In Progress.'))
        self.write({
            'state': 'completed',
            'completion_date': fields.Datetime.now(),
        })

    def action_cancel_repair(self):
        self.write({'state': 'rejected'})
    
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
        for part in self.part_ids:
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