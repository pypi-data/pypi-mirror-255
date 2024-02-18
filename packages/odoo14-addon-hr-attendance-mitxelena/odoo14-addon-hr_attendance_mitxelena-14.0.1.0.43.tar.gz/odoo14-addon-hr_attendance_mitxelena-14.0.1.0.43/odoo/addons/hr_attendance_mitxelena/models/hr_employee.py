from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    mother_calendar_id = fields.Many2one(
        "resource.calendar",
        domain="[('mother_calendar', '=', True)]",
        string="Shift Calendar",
        required=True,
    )

    def button_preview_attendance_report(self):
        self.ensure_one()
        context = dict(self.env.context, default_employee_id=self.id)
        return {
            "name": "Select Month for Report",
            "type": "ir.actions.act_window",
            "res_model": "attendance.report.wizard",
            "view_mode": "form",
            "view_id": self.env.ref(
                "hr_attendance_mitxelena.view_attendance_report_wizard_form"
            ).id,
            "target": "new",
            "context": context,
        }

    def assign_calendars_to_employees(self, month=None, year=None):
        if not year:
            year = fields.Date.today().year
        if not month:
            month = fields.Date.today().month
        # Get all mother calendars
        mother_calendars = self.env["resource.calendar"].search(
            [("mother_calendar", "=", True)]
        )
        for mother_calendar in mother_calendars:
            # Child calendar id
            calendar_ext_id = f"hr_attendance_mitxelena.calendar_{year}_{month}_{mother_calendar.hours_per_day}h"
            calendar_id = self.env["ir.model.data"].xmlid_to_res_id(calendar_ext_id)
            # Get employees with mother calendar
            employees = self.env["hr.employee"].search(
            [("mother_calendar_id", "=", mother_calendar.id)]
            )
            for employee in employees:
                employee.resource_calendar_id = calendar_id
               # logging.debug(f"Assigning {calendar_id.name} calendar to {employee.name} ")
    
    def restore_mother_calendars(self):
        employees = self.env["hr.employee"].search([])
        for employee in employees:
            employee.resource_calendar_id = employee.mother_calendar_id.id
            logging.debug(f"Assigning {employee.mother_calendar_id.name} calendar to {employee.name} ")
