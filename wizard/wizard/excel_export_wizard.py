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
        ('parts_requested', 'Parts Requested'),
        ('parts_arrived', 'Parts Arrived'),
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
        headers = ['Job Card', 'Customer', 'Brand', 'Model', 'Total Amount', 'Status', 'Warranty', 'Created Date']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        for row, card in enumerate(job_cards, 1):
            worksheet.write(row, 0, card.name, cell_format)
            worksheet.write(row, 1, card.customer_id.name if card.customer_id else '', cell_format)
            worksheet.write(row, 2, card.brand_id.name if card.brand_id else '', cell_format)
            worksheet.write(row, 3, card.model_id.name if card.model_id else '', cell_format)
            worksheet.write(row, 4, card.total_amount, num_format)
            worksheet.write(row, 5, dict(card._fields['state'].selection).get(card.state), cell_format)
            worksheet.write(row, 6, 'Yes' if card.warranty else 'No', cell_format)
            worksheet.write(row, 7, card.create_date.strftime('%Y-%m-%d') if card.create_date else '', cell_format)
        
        # Adjust columns
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:D', 20)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:H', 15)
        
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