# Security Verification Checklist (Odoo 18)

This module relies on **defense-in-depth**:
- **Menus** restricted by groups (UI visibility)
- **Actions/Reports/Wizards** restricted by groups (prevents direct action/report URL use)
- **ACLs** (model CRUD)
- **Record rules** (row-level access)
- **Server-side checks** for the dashboard JSON route and specific business constraints

Use this checklist after install/upgrade to confirm security behavior per role.

---

## 0) Pre-flight

1. Ensure the module is installed/updated:
   - Apps → upgrade **Mobile Repair Management**
2. Enable Developer Mode (Settings → activate developer mode).
3. Create a few demo records:
   - At least 2 Job Cards with different states: `draft`, `approved`, `in_progress`
   - Assign one Job Card to a Team and members (so technician record rules can be validated)
   - Add both billable parts and condemned parts
   - Ensure one Job Card has an Invoice and Payment state (for non-warranty path)

---

## 1) Test Users (recommended)

Create 6 users and assign **only one** repair role group each (plus the standard internal user permission as required by Odoo):

- U1: Repair / Manager → `mobile_repair_management.group_repair_manager`
- U2: Repair / Lead → `mobile_repair_management.group_repair_lead`
- U3: Repair / CSR → `mobile_repair_management.group_repair_csr`
- U4: Repair / Technician → `mobile_repair_management.group_repair_technician`
- U5: Repair / Procurement → `mobile_repair_management.group_repair_procurement`
- U6: Repair / Accounting → `mobile_repair_management.group_repair_accounting`

Tip: keep passwords simple for testing, and name users like `mr_test_manager`, etc.

---

## 2) Navigation / Menu visibility

Log in as each user and confirm:

- All repair roles (U1–U6) can see:
  - Mobile Repair root menu
  - Job Cards menu
- Only **Manager + Lead** can see **Configuration**:
  - Brands / Series / Models
  - Teams
  - Services
- Only **Manager + Lead + Procurement** can see **Damaged / Condemned Parts** report menu.
- Only **Manager + Lead** can see **Excel Report** wizard menu.

Expected: users outside a menu’s groups should not see it at all.

---

## 3) Direct Action/Report access (defense-in-depth)

Even if a user pastes an action/report URL, access should be denied by group restrictions.

### 3.1 Window actions
As U3/U4/U5/U6, try to open a restricted action by URL (example pattern):

- `/web#action=<xmlid>` is not stable across DBs, but you can test via:
  - Settings → Technical → Actions → Window Actions (developer mode)
  - Search the action (e.g., `Brands`, `Services`) and click it.

Expected:
- Users not in the action’s allowed groups should get an access warning / forbidden behavior.

### 3.2 Report action
As any repair role, open a Job Card and try Print → **Job Card / Quotation**.

Expected:
- Allowed repair roles can print.
- Non-repair internal users (if any exist) should not be able to print the report.

---

## 4) Record Rules (row-level access)

### 4.1 Technician job-card scoping
Log in as U4 (Technician):

- Open Job Cards list.
- Confirm you only see job cards where you are either:
  - in `assigned_member_ids`, OR
  - in the selected team’s `member_ids`

Expected: technician cannot browse unrelated job cards.

### 4.2 CSR state scoping
Log in as U3 (CSR):

- Confirm you can only see/edit Job Cards in states: `draft`, `requested`, `quotation`.

Expected: approved/in-progress/completed job cards should not be accessible.

### 4.3 Procurement state scoping
Log in as U5 (Procurement):

- Confirm you can only access Job Cards in states: `approved`, `in_progress`.
- Confirm you are read-only on Job Cards (based on ACL/rules).

### 4.4 Accounting read-only
Log in as U6 (Accounting):

- Confirm Job Cards are readable.
- Confirm you cannot modify Job Cards or delete them.

---

## 5) Button visibility & behavior (Job Card form)

Open a Job Card form as each role and confirm buttons shown/hidden:

- Quotation flow buttons:
  - **Generate Quotation**: Manager, Lead, CSR
- Billing flow buttons:
  - **Create Invoice**: Manager, Lead, Accounting
  - **Register Payment**: Manager, Accounting
- Work execution buttons:
  - **Assign Team**: Manager, Lead
  - **Start Repair / Complete Repair**: Manager, Lead, Technician
- Cancellation:
  - **Cancel**: Manager, Lead, CSR

Expected:
- Buttons should not appear for roles that should not run those actions.
- If a role can see a button, the action should succeed only when business prerequisites are met (invoice present, payment posted, team assigned, etc.).

---

## 6) Warehouse condemned restriction (business + security)

This is enforced server-side in the part line constraint:

- Log in as U5 (Procurement) and try to set a condemned part’s scope to **warehouse**.
  - Expected: allowed.
- Log in as U3 (CSR) or U4 (Technician) and try the same.
  - Expected: blocked with an error (permission constraint).

Also confirm “customer condemned” remains usable per your workflow.

---

## 7) Dashboard endpoint authorization

The JSON route is `auth='user'` and additionally checks repair-group membership.

Test:
- As U1–U6, open the dashboard view and confirm charts load.
- As a non-repair internal user (if you create one), confirm:
  - Dashboard data does not load
  - `/mobile_repair/dashboard_data` returns an AccessError

---

## 8) Regression checklist (quick)

- No XML errors on module upgrade.
- Kanban view loads without Owl errors.
- Assets load (CSS/JS for dashboard + styling).

---

## 9) If something fails

Capture:
- User + group
- The exact operation (menu/action/button/report)
- Odoo server logs stack trace

Then fix should usually be in one of:
- `security/security/ir.model.access.csv`
- `security/security/record_rules.xml`
- menu/action/report `groups` / `groups_id`
- server-side business constraints in Python
