{
    'name': 'Mobile Repair Management',
    'version': '18.0.1.0.0',
    'category': 'Services/Repair',
    'summary': 'Complete Mobile Repair Management System',
    'description': """
Mobile Repair Management System
===============================
Comprehensive solution for mobile repair operations: job cards, quotations,
spare parts, teams, pickings, invoicing and reports.
""",
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'images': ['static/description/icon.png'],
    'depends': [
        'base',
        'sale',
        'stock',
        'account',
        'project',
        'mail',
        'web',
    ],
    'data': [
        'security/security/groups.xml',
        'security/security/ir.model.access.csv',
        'data/data/data.xml',

        'views/assign_team_wizard_views.xml',
        'views/excel_report_wizard_views.xml',
        'views/views/device_views.xml',
        'views/views/service_views.xml',
        'views/views/team_views.xml',
        'views/views/job_card_views.xml',
        'views/views/menus.xml',

        'reports/reports/job_card_report.xml',
        'reports/reports/job_card_report_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mobile_repair_management/static/src/css/repair_style.css',
            'mobile_repair_management/static/src/js/repair_dashboard.js',
        ],
    },
    'demo': [],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
