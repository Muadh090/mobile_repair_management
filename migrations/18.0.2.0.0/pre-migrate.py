"""Pre-migration: remove obsolete security groups from the 6-group design.

The old design had 6 flat groups:
  - group_repair_csr
  - group_repair_lead
  - group_repair_procurement
  - group_repair_accounting
  - group_repair_technician (kept, redefined)
  - group_repair_manager    (kept, redefined)

The new design uses a 3-tier hierarchy:
  - group_repair_user       (new)
  - group_repair_technician (redefined, implies user)
  - group_repair_manager    (redefined, implies technician)

This migration removes the 4 obsolete groups and their related
ACLs, record rules, and ir.model.data entries so that the module
upgrade does not fail on dangling references.
"""
import logging

_logger = logging.getLogger(__name__)

OLD_GROUP_XMLIDS = [
    'group_repair_csr',
    'group_repair_lead',
    'group_repair_procurement',
    'group_repair_accounting',
]


def migrate(cr, version):
    if not version:
        return

    _logger.info("Cleaning up obsolete repair security groups...")

    for xmlid in OLD_GROUP_XMLIDS:
        # Find the res_id from ir.model.data
        cr.execute("""
            SELECT res_id FROM ir_model_data
            WHERE module = 'mobile_repair_management'
              AND name   = %s
              AND model  = 'res.groups'
        """, (xmlid,))
        row = cr.fetchone()
        if not row:
            _logger.info("  %s: already removed, skipping.", xmlid)
            continue

        group_id = row[0]
        _logger.info("  Removing %s (id=%s)...", xmlid, group_id)

        # Remove ACL entries referencing this group
        cr.execute("DELETE FROM ir_model_access WHERE group_id = %s", (group_id,))

        # Remove record rule links (ir.rule ↔ res.groups m2m)
        cr.execute("DELETE FROM rule_group_rel WHERE group_id = %s", (group_id,))

        # Remove group from users (res.groups ↔ res.users m2m)
        cr.execute("DELETE FROM res_groups_users_rel WHERE gid = %s", (group_id,))

        # Remove implied_ids links
        cr.execute("DELETE FROM res_groups_implied_rel WHERE gid = %s OR hid = %s",
                   (group_id, group_id))

        # Remove menu access links
        cr.execute("DELETE FROM ir_ui_menu_group_rel WHERE gid = %s", (group_id,))

        # Remove view group links
        cr.execute("DELETE FROM ir_ui_view_group_rel WHERE group_id = %s", (group_id,))

        # Remove act_window group links
        cr.execute("DELETE FROM ir_act_window_group_rel WHERE gid = %s", (group_id,))

        # Remove the ir.model.data entry
        cr.execute("""
            DELETE FROM ir_model_data
            WHERE module = 'mobile_repair_management'
              AND name   = %s
              AND model  = 'res.groups'
        """, (xmlid,))

        # Finally remove the group itself
        cr.execute("DELETE FROM res_groups WHERE id = %s", (group_id,))

    # Also clean up old record rule XML IDs that no longer exist
    old_rule_xmlids = [
        'rule_job_card_lead',
        'rule_job_card_csr',
        'rule_job_card_procurement',
        'rule_job_card_accounting',
        'rule_job_card_technician',
        'rule_job_card_part_line_lead',
        'rule_job_card_part_line_technician',
        'rule_job_card_part_line_csr',
        'rule_job_card_part_line_procurement',
        'rule_job_card_service_line_lead',
        'rule_job_card_service_line_technician',
        'rule_job_card_service_line_csr',
        'rule_timesheet_lead',
        'rule_timesheet_accounting',
    ]
    for xmlid in old_rule_xmlids:
        cr.execute("""
            SELECT res_id FROM ir_model_data
            WHERE module = 'mobile_repair_management'
              AND name   = %s
              AND model  = 'ir.rule'
        """, (xmlid,))
        row = cr.fetchone()
        if not row:
            continue
        rule_id = row[0]
        _logger.info("  Removing old rule %s (id=%s)...", xmlid, rule_id)
        cr.execute("DELETE FROM rule_group_rel WHERE rule_group_id = %s", (rule_id,))
        cr.execute("DELETE FROM ir_rule WHERE id = %s", (rule_id,))
        cr.execute("""
            DELETE FROM ir_model_data
            WHERE module = 'mobile_repair_management'
              AND name   = %s
              AND model  = 'ir.rule'
        """, (xmlid,))

    # Clean up old ACL ir.model.data entries
    old_acl_names = [
        'access_repair_brand_lead',
        'access_repair_series_lead',
        'access_repair_model_lead',
        'access_repair_team_lead',
        'access_repair_service_lead',
        'access_job_card_lead',
        'access_job_card_csr',
        'access_job_card_technician',
        'access_job_card_procurement',
        'access_job_card_accounting',
        'access_job_card_service_line_lead',
        'access_job_card_service_line_technician',
        'access_job_card_service_line_csr',
        'access_job_card_part_line_lead',
        'access_job_card_part_line_technician',
        'access_job_card_part_line_csr',
        'access_job_card_part_line_procurement',
        'access_repair_timesheet_lead',
        'access_repair_timesheet_accounting',
        'access_excel_report_wizard_lead',
        'access_assign_team_wizard_lead',
        'access_timesheet_wizard_manager',
        'access_timesheet_wizard_lead',
    ]
    for name in old_acl_names:
        cr.execute("""
            SELECT res_id FROM ir_model_data
            WHERE module = 'mobile_repair_management'
              AND name   = %s
              AND model  = 'ir.model.access'
        """, (name,))
        row = cr.fetchone()
        if row:
            _logger.info("  Removing old ACL %s (id=%s)...", name, row[0])
            cr.execute("DELETE FROM ir_model_access WHERE id = %s", (row[0],))
            cr.execute("""
                DELETE FROM ir_model_data
                WHERE module = 'mobile_repair_management'
                  AND name   = %s
                  AND model  = 'ir.model.access'
            """, (name,))

    _logger.info("Old security group cleanup complete.")
