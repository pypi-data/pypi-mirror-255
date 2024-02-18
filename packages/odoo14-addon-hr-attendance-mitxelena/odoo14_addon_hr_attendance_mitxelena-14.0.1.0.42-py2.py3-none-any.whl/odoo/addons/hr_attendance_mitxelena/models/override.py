from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

from datetime import datetime, time, timedelta
from collections import defaultdict
from odoo.tools import float_utils
from datetime import datetime, timedelta
from pytz import timezone, UTC

ROUNDING_FACTOR = 16


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """Returns a float equals to the timedelta between two dates given as string."""
        total_days = 0
        current_day = date_from.date() + timedelta(days=1) # We didn't want to do this, but... UTC
        limit_day = date_to.date()
        while current_day <= limit_day:
            not_weekend = current_day.weekday() < 5
            not_holiday = not self.env["hr.holidays.public"].is_public_holiday(
                current_day
            )
            if not_weekend and not_holiday:
                total_days += 1
            current_day += timedelta(days=1)

        hours_per_day = (
            self.env["hr.employee"]
            .browse(employee_id)
            .resource_calendar_id.hours_per_day
        )

        if self.request_unit_hours:
            custom_hours = (date_to - date_from).seconds / 3600.0
            total_days = 1
            hours_per_day = custom_hours

        elif self.request_unit_half and total_days != 0:
            total_days = 0.5

        # Ingenious, but it does not take into account holidays and weekends
        # total_days += (date_to - date_from).seconds / 3600.0 / hours_per_day
        return {"days": total_days, "hours": total_days * hours_per_day}

    @api.depends("number_of_days")
    def _compute_number_of_hours_display(self):
        for holiday in self:
            calendar = holiday._get_calendar()
            if holiday.date_from and holiday.date_to:
                number_of_hours = holiday._get_number_of_days(
                    holiday.date_from, holiday.date_to, holiday.employee_id.id
                )["hours"]
                holiday.number_of_hours_display = number_of_hours
            else:
                holiday.number_of_hours_display = 0

    @api.depends("number_of_hours_display")
    def _compute_number_of_hours_text(self):
        for leave in self:
            if leave.request_unit_half or leave.request_unit_hours:
                hours = int(leave.number_of_hours_display)
                minutes = int((leave.number_of_hours_display - hours) * 60)
                leave.number_of_hours_text = "%02d:%02d %s" % (
                    hours,
                    minutes,
                    _("Hours"),
                )
            else:
                leave.number_of_hours_text = "(%g %s)" % (
                    float_round(leave.number_of_hours_display, precision_digits=2),
                    _("Hours"),
                )
