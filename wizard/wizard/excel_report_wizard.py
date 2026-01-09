from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
import io
from datetime import datetime

class ExcelReportWizard(models.TransientModel):
    _name = 'excel.report.wizard'
    _description = 'Excel Report Wizard'
    
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    state = fields.Selection([
        ('all', 'All'),
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('quotation', 'Quotation'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ], string='Status', default='all')
    warranty = fields.Selection([
        ('all', 'All'),
        ('warranty', 'Warranty Only'),
        ('non_warranty', 'Non-Warranty Only'),
    ], string='Warranty Status', default='all')
    team_id = fields.Many2one('repair.team', string='Team')
    brand_id = fields.Many2one('repair.brand', string='Brand')
    
    excel_file = fields.Binary(string='Excel File', readonly=True)
    filename = fields.Char(string='Filename', readonly=True)
    
    def action_generate_report(self):
        domain = [
            ('create_date', '>=', self.date_from),
            ('create_date', '<=', self.date_to),
        ]
        
        if self.state != 'all':
            domain.append(('state', '=', self.state))
        
        if self.warranty == 'warranty':
            domain.append(('warranty', '=', True))
        elif self.warranty == 'non_warranty':
            domain.append(('warranty', '=', False))
        
        if self.team_id:
            domain.append(('team_id', '=', self.team_id.id))
        
        if self.brand_id:
            domain.append(('brand_id', '=', self.brand_id.id))
        
        job_cards = self.env['job.card'].search(domain)
        
        if not job_cards:
            raise UserError(_('No job cards found for the selected criteria.'))
        
        # Create Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Job Cards')
        
        # Formats
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#875A7B', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        
        cell_format = workbook.add_format({'border': 1, 'align': 'left'})
        num_format = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0.00'})
        
        # Headers
        headers = [
            'Job Card', 'Customer', 'Brand', 'Series', 'Model', 'IMEI', 'Problem Description',
            'Assigned Technicians', 'Responsible',
            'Service(s)', 'Service Charge(s)',
            'Part(s)', 'Unit Price', 'Part Qty', 'Available Stock',
            'Customer Condemned Part(s)', 'Warehouse Condemned Part(s)',
            'Total Amount', 'Status', 'Warranty', 'Created Date'
        ]
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        for row, card in enumerate(job_cards, 1):
            services = ', '.join([s.service_id.name for s in card.service_ids])
            service_charges = ', '.join([f"{s.price}" for s in card.service_ids])
            used_parts = card.part_ids.filtered(lambda l: l.condition_status != 'condemned')
            parts = ', '.join([p.product_id.display_name for p in used_parts])
            part_unit_prices = ', '.join([f"{p.unit_price}" for p in used_parts])
            part_quantities = ', '.join([f"{p.quantity}" for p in used_parts])
            part_stock = ', '.join([f"{p.stock_available}" for p in used_parts])
            cust_condemned = ', '.join([p.product_id.display_name for p in card.part_ids.filtered(lambda l: l.condition_status == 'condemned' and l.condemned_scope == 'customer')])
            wh_condemned = ', '.join([p.product_id.display_name for p in card.part_ids.filtered(lambda l: l.condition_status == 'condemned' and l.condemned_scope == 'warehouse')])
            technicians = ', '.join([u.name for u in card.assigned_member_ids])
            responsible = card.team_id.manager_id.name if card.team_id and card.team_id.manager_id else ''

            worksheet.write(row, 0, card.name, cell_format)
            worksheet.write(row, 1, card.customer_id.name if card.customer_id else '', cell_format)
            worksheet.write(row, 2, card.brand_id.name if card.brand_id else '', cell_format)
            worksheet.write(row, 3, card.series_id.name if card.series_id else '', cell_format)
            worksheet.write(row, 4, card.model_id.name if card.model_id else '', cell_format)
            worksheet.write(row, 5, card.imei or '', cell_format)
            worksheet.write(row, 6, card.problem_description or '', cell_format)
            worksheet.write(row, 7, technicians, cell_format)
            worksheet.write(row, 8, responsible, cell_format)
            worksheet.write(row, 9, services, cell_format)
            worksheet.write(row, 10, service_charges, cell_format)
            worksheet.write(row, 11, parts, cell_format)
            worksheet.write(row, 12, part_unit_prices, cell_format)
            worksheet.write(row, 13, part_quantities, cell_format)
            worksheet.write(row, 14, part_stock, cell_format)
            worksheet.write(row, 15, cust_condemned, cell_format)
            worksheet.write(row, 16, wh_condemned, cell_format)
            worksheet.write(row, 17, card.total_amount, num_format)
            worksheet.write(row, 18, dict(card._fields['state'].selection).get(card.state), cell_format)
            worksheet.write(row, 19, 'Yes' if card.warranty else 'No', cell_format)
            worksheet.write(row, 20, card.create_date.strftime('%Y-%m-%d') if card.create_date else '', cell_format)
        
        # Adjust columns
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:H', 18)
        worksheet.set_column('I:Q', 18)
        worksheet.set_column('R:U', 15)
        
        workbook.close()
        output.seek(0)
        
        # Save
        filename = f'Job_Cards_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        self.write({
            'excel_file': base64.b64encode(output.read()),
            'filename': filename,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/excel.report.wizard/{self.id}/excel_file/{filename}?download=true',
            'target': 'self',
        }