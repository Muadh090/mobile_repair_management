# Quick Start Guide - Mobile Repair Management Module

## 🚀 Get Running in 5 Minutes

### Step 1: Copy Module
```bash
cp -r c:\mobile_repair_management "C:\Program Files\Odoo\addons\"
```

Or update your `odoo.conf` addons_path:
```ini
addons_path = C:/Program Files/Odoo/addons,c:/mobile_repair_management
```

### Step 2: Start Odoo

**Windows (PowerShell)**:
```powershell
cd c:\mobile_repair_management
.\run_odoo.ps1 -OdooBin "C:\Program Files\Odoo 18\odoo-bin"
```

**Windows (Batch)**:
```cmd
cd c:\mobile_repair_management
start_odoo.bat
```

**Linux/Mac**:
```bash
python odoo-bin -c odoo.conf
```

### Step 3: Install Module
1. Open **http://localhost:8069**
2. Log in with **admin / admin**
3. Go to **Apps** (top-left menu)
4. Search: **"Mobile Repair"**
5. Click **Install**

---

## 📋 First-Time Setup (10 min)

### Add Master Data:

**1. Create Brands**
- Menu: **Mobile Repair** → **Configuration** → **Brands**
- Add: "Apple", "Samsung", "Xiaomi", etc.
- Upload logo image (optional)

**2. Add Series**
- Select Brand → **Series** tab
- Add: "iPhone 12", "Galaxy S21", etc.

**3. Add Models**
- Select Series → **Models** tab
- Add: "iPhone 12 Pro Max", "Galaxy S21 Ultra", etc.

**4. Create Services**
- Menu: **Mobile Repair** → **Services**
- Add services with pricing:
  - Screen Replacement: $150
  - Battery Replacement: $80
  - Motherboard Service: $300

**5. Create Teams**
- Menu: **Mobile Repair** → **Teams**
- Add team with members (users from res.users)
- Assign manager
- Link project (optional)

---

## 🔧 Create Your First Job Card

**Menu: Mobile Repair** → **Job Cards** → **New**

1. **Customer**: Select or create a customer
2. **Device**: Choose Brand → Series → Model
3. **Problem**: Describe the issue
4. **Services**: Click "Add" and select repair services
5. **Parts**: Click "Add" and add any spare parts needed
6. **Save**

---

## ✅ Complete a Job Card Workflow

### Stage 1: Draft → Requested
- Click **Mark as Requested**

### Stage 2: Requested → Quotation
- Click **Generate Quotation** (if not warranty)
- System generates professional PDF

### Stage 3: Quotation → Approved
- Customer approves (in form, set "Customer Approval" to "Approved")
- Click **Request Parts** button

### Stage 4: Parts Requested → Parts Arrived
- Go to **Stock** → **Picking** (from stat button)
- Click **Validate** to mark picking done
- Job card auto-updates to "Parts Arrived"

### Stage 5: Parts Arrived → In Progress
- Click **Assign Team**
- Select repair team and members
- Set expected duration
- Click **Assign Team**
- Status moves to "In Progress"

### Stage 6: In Progress → Completed
- Click **Complete Repair**

### Stage 7: Completed → Invoiced
- Click **Create Invoice**
- Click **Register Payment** (optional, for payment tracking)

---

## 📊 Dashboard & Reports

**Dashboard**: **Mobile Repair** → **Dashboard**
- See KPIs, charts by status, inspection type, delivery type
- Monthly revenue chart

**Excel Report**: **Mobile Repair** → **Reports** → **Excel Report**
- Select date range
- Filter by status, warranty, team, brand
- Export to Excel

**PDF Report**: Open any job card → **Print** → **Job Card / Quotation**

---

## 🔐 User Access Control

Default groups:
- **Repair / Manager** — Full access
- **Repair / Lead** — Configuration + supervisory actions
- **Repair / CSR** — Draft/request/quotation handling
- **Repair / Technician** — Assigned-job work execution
- **Repair / Procurement** — Approved/in-progress visibility (warehouse condemned control)
- **Repair / Accounting** — Read-only job cards + billing actions

To assign users to groups:
1. **Settings** → **Users & Companies** → **Users**
2. Select user
3. **Access Rights** tab
4. Add the appropriate group under the *Repair* category

Security verification checklist:
- See **SECURITY_VERIFICATION_CHECKLIST.md**

---

## 🛠️ Common Customizations

### Change Tax Rate
Edit: `models/models/job_card.py`
```python
tax_amount = subtotal * 0.20  # Change 0.15 to 0.20 for 20% tax
```
Then restart Odoo.

### Add Custom Field to Job Card
Edit: `models/models/job_card.py`
```python
custom_field = fields.Char(string='My Custom Field')
```
Restart Odoo and field appears automatically.

### Change Dashboard Colors
Edit: `static/src/css/repair_style.css`

---

## 🆘 Troubleshooting

**Module won't install?**
- Check Odoo log file: `odoo.log` (set in odoo.conf)
- Ensure dependencies installed: base, sale, stock, account, project

**Quotation not generating?**
- Verify job card is not marked as warranty
- Check PDF renderer installed: `pip install wkhtmltopdf` (or use default Odoo renderer)

**Picking not created?**
- Ensure warehouse exists in company
- Verify "Internal" picking type is configured

**Invoice has missing fields?**
- Check chart of accounts (at least one income account needed)
- Verify product categories have income accounts linked

---

## 📞 Need Help?

1. Check **INSTALLATION_AND_USAGE.md** for detailed docs
2. Review **IMPLEMENTATION_SUMMARY.md** for feature checklist
3. Check Odoo logs: `odoo.log`
4. Verify module status: **Apps** → search "Mobile Repair" → view status

---

**Odoo Version**: 18.0+  
**Module Version**: 18.0.1.0.0  
**Status**: Production-Ready ✓
