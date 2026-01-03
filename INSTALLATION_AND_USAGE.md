# Mobile Repair Management - Odoo 18 Module

A complete, production-ready **Odoo 18 module** for managing mobile device repairs, from job card creation through quotation, parts ordering, team assignment, work logging, invoicing, and comprehensive reporting.

## Features

### 1. **Dashboard** 
- Real-time KPI metrics (total job cards by status, inspection statistics)
- Pie charts for inspection types and delivery types
- Bar chart for invoiced amounts by month
- Status tracking across all repair stages

### 2. **Configuration Menu**
- **Device Management**: Brands, Series, Models with logo uploads and detailed specifications
- Fully searchable, with tree and form views
- Cascade dropdowns: Brand → Series → Model

### 3. **Teams Management**
- Team list with members and manager assignment
- Linked to project module for task tracking
- Computed fields: completed jobs count and average repair time
- Team-based color coding and performance metrics

### 4. **Services & Products**
- Repair services with pricing and duration tracking
- Service types: Basic, Premium, High-end, Motherboard, Screen, Battery, Software
- Kanban and form views for easy browsing

### 5. **Job Cards (Core Workflow)**
**Stages**: Draft → Requested → Quotation → Approved → Parts Requested → Parts Arrived → In Progress → Completed (or Rejected)

**Views**: Kanban, Tree, Form
**Features**:
- Customer details with linked res.partner
- Device information (IMEI, accessories, condition)
- Warranty management
- Services and spare parts list with automatic totals
- Tax calculation (15% default)

### 6. **Quotation Workflow**
- Auto-generated quotation from job card services/parts
- Professional PDF quotation report (with terms & conditions)
- Customer approval/rejection workflow
- Automatic stage transitions

### 7. **Stock Picking Integration**
- **Request Parts** button creates automatic stock pickings
- Moves from Main Warehouse → Team/Internal Location
- Picking status: Waiting → Ready → Done
- Auto-updates job card to "Parts Arrived" on validation

### 8. **Team Assignment**
- Assign team and members to repair job
- Set expected duration
- Creates project task automatically
- Moves job to "In Progress"

### 9. **Timesheet & Work Log**
- Technician time tracking (hours, date, work description)
- Billable flag for cost tracking
- Linked to project timesheets and analytic lines

### 10. **Invoice Creation**
- Auto-generate account.move from services and parts
- Support for warranty vs. non-warranty invoices
- Payment registration with cash/bank/POS options
- Job card moves to "Completed" after payment

### 11. **Reports**
- **PDF Report**: Job card/quotation with customer, device, services, parts, totals
- **Excel Export Wizard**: Date range filters, status filters, warranty filters, warranty/non-warranty columns

### 12. **Security & Access**
- Role-based access (Manager, User, Technician)
- Model-level CRUD permissions
- Security groups defined in `security/security/groups.xml`

---

## Installation

### 1. **Prerequisites**
- Odoo 18 installed and running
- PostgreSQL database
- Python 3.10+

### 2. **Copy Module to Addons**
```bash
cp -r mobile_repair_management /path/to/odoo/addons/
```

Or update your `addons_path` in `odoo.conf`:
```ini
addons_path = /path/to/odoo/addons,c:/mobile_repair_management
```

### 3. **Create/Update Database**
Start Odoo with the module folder in `addons_path`:

**Using the provided script (Windows)**:
```powershell
cd c:\mobile_repair_management
.\run_odoo.ps1 -OdooBin "C:\Program Files\Odoo 18\odoo-bin"
```

Or double-click:
```
start_odoo.bat
```

**Manual command** (adjust paths):
```bash
C:\Program Files\Odoo 18\odoo-bin -c c:\mobile_repair_management\odoo.conf
```

### 4. **Install the Module in Odoo**
1. Open **http://localhost:8069**
2. Log in as `admin` (default password: `admin`)
3. Go to **Apps** → Search for **"Mobile Repair"**
4. Click **Install** on the module

---

## Configuration

### Edit `odoo.conf`
Located at: `c:\mobile_repair_management\odoo.conf`

Key settings to update:
```ini
addons_path = C:/Program Files/Odoo/addons,c:/mobile_repair_management
admin_passwd = admin                          # Master password (change in production!)
db_host = False                                # Set to 'localhost' for remote Postgres
db_port = False                                # Default: 5432
db_user = odoo                                # Postgres user
db_password = odoo                            # Postgres password
xmlrpc_port = 8069                            # HTTP port for Odoo
logfile = c:/mobile_repair_management/odoo.log
data_dir = c:/mobile_repair_management/.local/share/Odoo
```

---

## Usage Guide

### Step 1: Initialize Master Data
**Configurations** → **Brands, Series, Models**
- Create mobile brands (Apple, Samsung, etc.)
- Add series per brand (iPhone 12, iPhone 13, etc.)
- Add models (iPhone 12 Pro Max, etc.)

**Configurations** → **Services**
- Add repair services with pricing (e.g., "Screen Replacement - $150")

**Teams**
- Create repair teams and assign manager + members
- Link to a project (optional, for task tracking)

### Step 2: Create a Job Card
**Job Cards** → **New**
1. Select customer (link to res.partner)
2. Choose device (Brand → Series → Model)
3. Add problem description
4. Select inspection type and delivery type
5. Add services (from repair.service)
6. Add spare parts (from product.product)
7. Save and click **Mark as Requested**

### Step 3: Generate Quotation
Job Card form → **Generate Quotation** button
- Creates professional PDF quotation
- Sends to customer (optional email)
- Waits for approval/rejection

### Step 4: Request Parts (if approved)
Job Card → **Request Parts** button
- Creates stock picking automatically
- Moves to warehouse location
- Click "Validate" on picking to mark **Parts Arrived**

### Step 5: Assign Team & Start Repair
Job Card → **Assign Team** button
- Select team and members
- Set expected duration
- Creates project task automatically
- Moves to **In Progress**

### Step 6: Log Work/Timesheet
Within the job card's **Task & Work Log** tab:
- Technicians log hours spent, work done
- Auto-links to project timesheet

### Step 7: Complete & Invoice
Job Card form:
- **Complete Repair** button → moves to Completed stage
- **Create Invoice** button → auto-generates account.move
- **Register Payment** button → record payment and finish

---

## Workflow Diagram

```
Draft
  ↓
Requested (Mark as Requested)
  ↓
Quotation (Generate Quotation)
  ├→ Approved (Customer approves)
  │   ↓
  │   Parts Requested (Request Parts)
  │   ↓
  │   Parts Arrived (Validate picking)
  │   ↓
  │   In Progress (Assign Team)
  │   ↓
  │   Completed (Complete Repair → Create Invoice → Register Payment)
  │
  └→ Rejected (Customer rejects) → END
```

---

## File Structure

```
mobile_repair_management/
├── __init__.py
├── manifest.py
├── odoo.conf                              # Config for running Odoo
├── run_odoo.ps1                           # PowerShell launcher
├── start_odoo.bat                         # Windows batch launcher
│
├── models/
│   ├── __init__.py
│   ├── job_card_line.py                   # Service & Part line models
│   ├── repair_timesheet.py                # Timesheet model
│   └── models/
│       ├── __init__.py
│       ├── job_card.py                    # Core job card model
│       ├── repair_brand.py                # Brand model
│       ├── repair_series.py               # Series model
│       ├── repair_model.py                # Device model
│       ├── repair_team.py                 # Team model
│       ├── repair_service.py              # Service model
│       └── assign_team_wizard.py          # Assign team transient
│
├── wizard/
│   ├── __init__.py
│   ├── timesheet_wizard.py                # Timesheet entry wizard
│   ├── wizard/
│   │   ├── __init__.py
│   │   ├── excel_export_wizard.py         # Excel report wizard
│   │   └── excel_export_wizard.xml
│   └── wizards/
│       └── assign_team_wizard.py
│
├── views/
│   ├── assign_team_wizard_views.xml       # Wizard views
│   ├── excel_report_wizard_views.xml
│   ├── menus.xml                          # Menu definitions (top-level)
│   └── views/
│       ├── assets.xml                     # CSS/JS assets
│       ├── dashboard_views.xml            # Dashboard
│       ├── device_views.xml               # Brand/Series/Model views
│       ├── service_views.xml              # Service views
│       ├── team_views.xml                 # Team views
│       └── job_card_views.xml             # Job card views
│
├── reports/
│   ├── __init__.py
│   └── reports/
│       ├── __init__.py
│       ├── job_card_report.py             # Report model
│       ├── job_card_report.xml            # Report action
│       └── job_card_report_template.xml   # QWeb template
│
├── security/
│   └── security/
│       ├── groups.xml                     # Custom security groups
│       └── ir.model.access.csv            # CRUD permissions
│
├── data/
│   └── data/
│       └── data.xml                       # Default sequences and data
│
├── static/
│   └── src/
│       ├── css/
│       │   ├── repair_style.css           # Module styles
│       │   └── repair_dashboard.css
│       └── js/
│           └── repair_dashboard.js        # Dashboard JS
│
└── controllers/
    └── controllers/
        ├── main.py
        └── dashboard_controller.py
```

---

## Key Models & Fields

### `job.card`
- `name` - Auto-generated job card number (sequence)
- `state` - Selection (draft, requested, quotation, approved, parts_requested, in_progress, completed, rejected)
- `customer_id` - Many2one(res.partner)
- `brand_id`, `series_id`, `model_id` - Device hierarchy
- `service_ids` - One2many(job.card.service.line)
- `part_ids` - One2many(job.card.part.line)
- `team_id` - Many2one(repair.team)
- `picking_id` - Many2one(stock.picking)
- `invoice_id` - Many2one(account.move)
- `warranty` - Boolean
- `total_amount` - Float (computed)

### `repair.team`
- `name`, `manager_id`, `member_ids`
- `project_id` - Many2one(project.project)
- `completed_jobs` - Integer (computed)
- `avg_repair_time` - Float (computed)

### `repair.service`
- `name`, `service_type`, `price`, `duration`
- `product_id` - Many2one(product.product, optional link)

### `repair.brand` / `repair.series` / `repair.model`
- Hierarchical device structure
- Logo/image support
- Specifications and common issues documentation

### `repair.timesheet`
- `job_card_id`, `user_id` (technician)
- `date`, `duration`, `description` (work done)
- `is_billable` - Boolean

---

## Customization & Extensions

### Add Custom Fields
Edit the respective model files in `models/models/` and add fields:
```python
custom_field = fields.Char(string='Custom Field')
```
No database migration needed — Odoo creates columns on install/upgrade.

### Modify Tax Rate
In `job_card.py`, update the `_compute_totals` method:
```python
tax_amount = subtotal * 0.20  # Change from 0.15 (15%) to 0.20 (20%)
```

### Change Dashboard Colors
Edit `static/src/css/repair_style.css` or `repair_dashboard.js`.

---

## Troubleshooting

### Module Installation Fails
- **Check logs**: Look in `odoo.log` (path in `odoo.conf`)
- **Verify dependencies**: Ensure base, sale, stock, account, project modules are installed
- **Check model IDs**: Run `SELECT * FROM ir_model WHERE model LIKE 'job%';` in Postgres

### Quotation Report Not Generating
- Ensure `reports/reports/job_card_report.xml` is loaded
- Check report name matches: `mobile_repair_management.job_card_report_template`

### Stock Picking Not Creating
- Verify warehouse exists and has proper locations configured
- Check that `picking_type` with code `'internal'` exists

### Invoice Fields Missing
- Ensure `account.move` model is properly installed
- Check accounting chart of accounts in company settings

---

## Support & Documentation

- **Odoo 18 API**: https://www.odoo.com/documentation/18.0/
- **QWeb Templates**: https://www.odoo.com/documentation/18.0/developer/reference/frontend/qweb.html
- **Stock Picking**: https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/routes/overview/manage_routes.html

---

## License

**LGPL-3.0** — This module is free and open-source.

---

**Version**: 18.0.1.0.0  
**Last Updated**: December 2025
