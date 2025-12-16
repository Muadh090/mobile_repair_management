# Mobile Repair Management Module - Architecture & Design

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Odoo 18 Backend                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │            Controllers (HTTP Endpoints)                 │   │
│  │  - dashboard_controller.py  (dashboard data)           │   │
│  │  - main.py                 (API routes)                │   │
│  └────────────────────────────────────────────────────────┘   │
│                            ↓                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │               Business Logic (Models)                   │   │
│  │  ┌──────────────────────────────────────────┐          │   │
│  │  │ Core Models:                             │          │   │
│  │  │  • job.card (main workflow)              │          │   │
│  │  │  • repair.team (technician teams)        │          │   │
│  │  │  • repair.service (repair offerings)     │          │   │
│  │  │  • repair.brand/series/model (devices)   │          │   │
│  │  │  • repair.timesheet (time tracking)      │          │   │
│  │  └──────────────────────────────────────────┘          │   │
│  │  ┌──────────────────────────────────────────┐          │   │
│  │  │ Transient Models (Wizards):              │          │   │
│  │  │  • excel.report.wizard                   │          │   │
│  │  │  • assign.team.wizard                    │          │   │
│  │  │  • timesheet.wizard                      │          │   │
│  │  └──────────────────────────────────────────┘          │   │
│  │  ┌──────────────────────────────────────────┐          │   │
│  │  │ Line Models:                             │          │   │
│  │  │  • job.card.service.line                │          │   │
│  │  │  • job.card.part.line                   │          │   │
│  │  └──────────────────────────────────────────┘          │   │
│  └────────────────────────────────────────────────────────┘   │
│                            ↓                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                 Odoo Standard Models                    │   │
│  │  • res.partner (customers)                            │   │
│  │  • res.users (technicians, managers)                  │   │
│  │  • account.move (invoices)                            │   │
│  │  • stock.picking (parts warehouse)                    │   │
│  │  • project.task (repair tasks)                        │   │
│  │  • product.product (spare parts)                      │   │
│  └────────────────────────────────────────────────────────┘   │
│                            ↓                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │          PostgreSQL Database (Persistent)              │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Web UI)                          │
├─────────────────────────────────────────────────────────────────┤
│  • Kanban views (drag-and-drop workflow)                       │
│  • Tree views (list with hierarchy)                            │
│  • Form views (detailed editing)                               │
│  • Dashboard (KPI charts)                                      │
│  • PDF reports (quotations, job cards)                         │
│  • Excel export (bulk reporting)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow: Job Card Lifecycle

```
User Creates Job Card
        ↓
   ┌─────────────┐
   │    DRAFT    │  (Initial state)
   └──────┬──────┘
          ↓ (Mark as Requested)
   ┌──────────────────┐
   │   REQUESTED      │  (Awaiting quotation)
   └──────┬───────────┘
          ↓ (Generate Quotation)
   ┌──────────────────┐
   │   QUOTATION      │  (PDF sent to customer)
   └───┬──────────┬───┘
       │ Approved │ Rejected
       ↓          ↓
   ┌────────┐  ┌──────────┐
   │APPROVED│  │ REJECTED │ (End state)
   └───┬────┘  └──────────┘
       ↓ (Request Parts)
   ┌──────────────────────┐
   │ PARTS_REQUESTED      │  (Stock picking created)
   └───┬──────────────────┘
       ↓ (Stock validated)
   ┌──────────────────────┐
   │ PARTS_ARRIVED        │  (Parts ready for repair)
   └───┬──────────────────┘
       ↓ (Assign Team)
   ┌──────────────────────┐
   │ IN_PROGRESS          │  (Technicians working)
   │  ├─ Timesheet logged │  (Work hours tracked)
   │  └─ Task created     │  (Project linked)
   └───┬──────────────────┘
       ↓ (Complete Repair)
   ┌──────────────────────┐
   │ COMPLETED            │  (Repair done)
   │  ├─ Invoice created  │  (Services + parts billed)
   │  └─ Payment logged   │  (Cash/bank/POS)
   └──────────────────────┘
```

---

## 🔄 Workflow State Machine

```python
STATE_TRANSITIONS = {
    'draft': ['requested'],
    'requested': ['quotation'],
    'quotation': ['approved', 'rejected'],
    'approved': ['parts_requested'],
    'parts_requested': ['parts_arrived'],
    'parts_arrived': ['in_progress'],
    'in_progress': ['completed'],
    'completed': [],  # End state
    'rejected': [],   # End state
}
```

---

## 📁 Package Structure

```
mobile_repair_management/
│
├── models/                 # Data models
│   ├── __init__.py        # Import subpackage
│   ├── job_card_line.py   # Service & part line classes
│   ├── repair_timesheet.py # Timesheet class
│   └── models/
│       ├── __init__.py
│       ├── job_card.py                # CORE: Main job card model
│       ├── repair_brand.py            # Device brand hierarchy
│       ├── repair_series.py           # Device series hierarchy
│       ├── repair_model.py            # Device model hierarchy
│       ├── repair_team.py             # Team + member management
│       ├── repair_service.py          # Service catalog
│       └── assign_team_wizard.py      # Team assignment transient
│
├── wizard/                # Transient models (wizards)
│   ├── __init__.py
│   ├── timesheet_wizard.py            # Manual timesheet entry
│   ├── wizard/
│   │   ├── __init__.py
│   │   ├── excel_export_wizard.py     # CORE: Excel report export
│   │   └── excel_export_wizard.xml
│   └── wizards/
│       └── assign_team_wizard.py
│
├── views/                 # XML view definitions
│   ├── assign_team_wizard_views.xml
│   ├── excel_report_wizard_views.xml
│   ├── menus.xml                      # CORE: Menu structure
│   └── views/
│       ├── assets.xml                 # CSS/JS includes
│       ├── dashboard_views.xml        # CORE: Dashboard
│       ├── device_views.xml           # Brand/Series/Model views
│       ├── service_views.xml          # Service views
│       ├── team_views.xml             # Team views
│       └── job_card_views.xml         # CORE: Job card views
│
├── reports/               # QWeb PDF reports
│   ├── __init__.py
│   └── reports/
│       ├── __init__.py
│       ├── job_card_report.py         # Report model
│       ├── job_card_report.xml        # Report action
│       └── job_card_report_template.xml # CORE: QWeb template
│
├── security/              # Access control
│   └── security/
│       ├── groups.xml                 # Security groups
│       └── ir.model.access.csv        # CRUD permissions
│
├── data/                  # Demo/default data
│   └── data/
│       └── data.xml                   # Sequences & defaults
│
├── static/                # CSS/JS assets
│   └── src/
│       ├── css/
│       │   ├── repair_style.css       # Module styles
│       │   └── repair_dashboard.css
│       └── js/
│           └── repair_dashboard.js    # Dashboard interactivity
│
├── controllers/           # HTTP endpoints
│   ├── __init__.py
│   └── controllers/
│       ├── __init__.py
│       ├── main.py                    # API routes
│       └── dashboard_controller.py    # Dashboard data
│
├── manifest.py            # CORE: Module metadata
├── __init__.py            # CORE: Package root
├── odoo.conf              # Odoo configuration
├── run_odoo.ps1           # PowerShell launcher
├── start_odoo.bat         # Batch launcher
└── README.md              # (Optional) module readme
```

---

## 🎯 Key Design Decisions

### 1. **Staged Workflow**
- 9 stages to match real-world repair process
- Clear handoffs between departments (reception → quotation → parts → repair → billing)
- Each stage transition triggers business logic (pickling, invoicing, etc.)

### 2. **Modular Hierarchy: Device**
- Brand → Series → Model allows flexible product catalog
- Supports multiple devices (phone brands, tablet brands, etc.)
- Each level has image/spec support for rich UI

### 3. **Team-Based Assignment**
- Teams own jobs (not individual technicians)
- Team creation auto-links to project for task tracking
- Performance metrics (completed jobs, avg time) computed per team

### 4. **Stock Picking Integration**
- Reuses Odoo's built-in stock module (no reinvention)
- Automatic picking creation on "Request Parts"
- Status sync: Parts Requested → Parts Arrived via picking validation

### 5. **Wizard-Based Actions**
- Assign team, export reports, log timesheet as transient models
- Keeps forms clean, focuses on primary job card view
- Easy to extend with new wizards

### 6. **Computed Fields**
- Totals (service + parts + tax) auto-calculated
- Job card counts and metrics recomputed on save
- No manual aggregation needed

### 7. **Warranty Flag**
- Simple boolean checkbox
- Blocks quotation/invoice for warranty repairs (configurable)
- Allows warranty-only service tracking

---

## 🔐 Security Model

```
┌─────────────────────────────────────────┐
│       Repair / Manager                  │
│  (Full CRUD on all models)              │
│  ├── Create brands, services, teams    │
│  ├── Override job card actions         │
│  ├── Access all reports                │
│  └── Manage users & permissions        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       Repair / User                     │
│  (Read/write job cards, limited config) │
│  ├── Create & manage job cards         │
│  ├── View reports                      │
│  ├── Read-only on brands/services      │
│  └── Cannot delete records             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       Repair / Technician               │
│  (Minimal: time tracking & work logs)   │
│  ├── Log time on job cards             │
│  ├── View assigned tasks               │
│  ├── Cannot create/edit job cards      │
│  └── Cannot access config/reports      │
└─────────────────────────────────────────┘
```

---

## 🚀 Performance Considerations

### Indexed Fields (Recommended)
```sql
CREATE INDEX idx_job_card_state ON job_card(state);
CREATE INDEX idx_job_card_customer ON job_card(customer_id);
CREATE INDEX idx_job_card_team ON job_card(team_id);
CREATE INDEX idx_job_card_create_date ON job_card(create_date);
```

### Aggregation Queries
- Dashboard KPIs computed on-demand (consider caching for > 10k records)
- Timesheet summaries use Odoo's built-in analytic module

### Stock Moves
- Picking creation is fast (standard Odoo operation)
- Validate in background for large operations

---

## 🔌 Integration Points

### With Odoo Standard Modules
- **stock**: Warehouse, pickings, moves (parts request)
- **account**: Invoices, payment methods, tax (invoicing)
- **project**: Tasks, timesheets, projects (team tasks)
- **sale**: Not directly (custom job card flow, but can be extended)
- **res.partner**: Customers
- **product**: Spare parts, services (product.product)

### External Integration (Possible Extensions)
- **SMS/Email**: Quotation notifications
- **POS**: Payment processing
- **Accounting**: Bank reconciliation for payments
- **Analytics**: BI dashboards (Power BI, Metabase)

---

## 📈 Scaling & Customization

### Add New Stages
Edit `models/models/job_card.py`:
```python
state = fields.Selection([
    ... existing stages ...
    ('quality_check', 'Quality Check'),  # New stage
    ('shipping', 'Shipping'),             # New stage
], ...)
```

### Add New Reports
Create new report in `reports/reports/`:
1. Python model (AbstractModel)
2. QWeb template
3. Report action in XML

### Add Custom Workflows
Override action methods in `job_card.py`:
```python
def action_complete_repair(self):
    # Add custom logic here
    super().action_complete_repair()
    # Or create new stages with custom transitions
```

---

## 🧪 Testing Strategy

### Unit Tests (Recommended)
- Model creation, field validation
- Workflow transitions
- Computed field calculations

### Integration Tests
- Stock picking creation
- Invoice generation
- Report rendering

### User Acceptance Tests
- End-to-end job card workflow
- Dashboard rendering
- Multi-user scenarios (permissions)

---

**Architecture Version**: 1.0  
**Last Updated**: December 15, 2025  
**Odoo Target**: 18.0+
