import datetime
import logging

from odoo import api, fields, models

from ..helpers.calendar import compute_year_bussiness_days

_logger = logging.getLogger(__name__)


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    bussiness_days = fields.Integer(
        name="Bussiness Days",
        default=0,
        help="Number of bussiness days in the calendar.",
    )
    mother_calendar = fields.Boolean(
        name="Master calendar",
        default=False,
        help="Check if this calendar is intended to be replicated every month.",
    )

    from_calendar = fields.Many2one(
        "resource.calendar", string="From calendar", ondelete="cascade"
    )

    child_calendars = fields.One2many(
        "resource.calendar",
        "from_calendar",
        string="Child calendars",
        ondelete="cascade",
    )

    @api.depends("bussiness_days", "hours_per_day")
    def _compute_total_hours(self):
        for rec in self:
            rec.total_hours = rec.bussiness_days * rec.hours_per_day

    def compute_yearly_resource_calendars(self, year=None):
        """
        Create resource calendars for a given year.
        If no year is given, the current year will be used.
        Holidays are taken from hr.public.holidays model and discarded from bussiness days.
        """

        if year is None:
            year = datetime.date.today().year
        public_holidays = self.env["hr.holidays.public"].search([("year", "=", year)])
        holidays = []
        for holiday in public_holidays:
            for line in holiday.line_ids:
                holidays.append(line.date)

        # Compute bussiness days per month
        monthly_bussiness_days = compute_year_bussiness_days(year, holidays)

        # Create resource calendars for month and type of calendar
        for month, bussiness_days in monthly_bussiness_days.items():
            self._create_monthly_calendars(month, year, bussiness_days)

    def _create_monthly_calendars(self, month, year, bussiness_days):
        # Get all mother calendars and create a monthly calendar for each one
        mother_calendars = self.search([("mother_calendar", "=", True)])
        for mother_calendar in mother_calendars:
            _logger.debug(
                f"Creating {mother_calendar.name} calendar for {month}/{year} "
            )
            external_id = f"hr_attendance_mitxelena.calendar_{year}_{month}_{mother_calendar.hours_per_day}h"
            calendar_external_id = self.env["ir.model.data"].xmlid_to_res_id(external_id)
            if calendar_external_id:
                _logger.debug(
                    f"Calendar {mother_calendar.name} for {month}/{year} already exists"
                )
                continue
            # Generate attendance ids for the new calendar: copy from mother calendar
            attendance_ids = mother_calendar.attendance_ids
            new_attendance_ids = []
            
            calendar = self.env["resource.calendar"].create(
                {
                    "name": f"[{month}/{year}]: for {mother_calendar.name}",
                    "bussiness_days": bussiness_days,
                    "hours_per_day": mother_calendar.hours_per_day,
                    "from_calendar": mother_calendar.id,
                    "attendance_ids": [],
                }
            )
            calendar_id = calendar.id

            for attendance in attendance_ids:
                attendance_id = attendance.id
                attendance_ids = self.env["resource.calendar.attendance"].create(
                    {
                        "name": f"{attendance.name} {month}/{year}",
                        "dayofweek": attendance.dayofweek,
                        "date_from": attendance.date_from,
                        "date_to": attendance.date_to,
                        "hour_from": attendance.hour_from,
                        "hour_to": attendance.hour_to,
                        "day_period": attendance.day_period,
                        "calendar_id": calendar_id,
                    }
                )
                new_attendance_ids.append(attendance_ids.id)

            self.env["ir.model.data"].create(
                {
                    "module": "hr_attendance_mitxelena",
                    "name": f"calendar_{year}_{month}_{mother_calendar.hours_per_day}h",
                    "model": "resource.calendar",
                    "res_id": calendar_id,
                    "noupdate": True,
                }
            )
