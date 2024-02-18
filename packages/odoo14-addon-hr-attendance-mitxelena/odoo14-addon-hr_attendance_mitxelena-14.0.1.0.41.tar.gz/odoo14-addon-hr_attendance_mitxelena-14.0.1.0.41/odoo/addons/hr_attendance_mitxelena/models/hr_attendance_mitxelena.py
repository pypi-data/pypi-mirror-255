from calendar import monthrange
from datetime import datetime, timedelta
from logging import getLogger

from pytz import timezone, utc
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.tools import config

_logger = getLogger(__name__)


class HrAttendanceMitxelena(models.Model):
    _inherit = "hr.attendance"

    def get_attendance_window(self):
        attendance_window = int(
            self.env["ir.config_parameter"].get_param("hr_attendance_window", 12)
        )
        if (
            self.employee_id.mother_calendar_id.id
            == "hr_attendance_mitxelena.office_calendar"
        ):
            office_plus = self.env["ir.config_parameter"].get_param(
                "hr_attendance_mitxelena.hr_attendance_window_plus_office", 6
            )
            attendance_window += office_plus
        return attendance_window

    date = fields.Date(compute="_compute_date", store=True)

    is_holiday = fields.Boolean(compute="_compute_is_holiday", store=True)

    is_relevo = fields.Boolean(compute="_compute_is_relevo", store=True)

    no_recompute = fields.Boolean(default=False)

    # Fields to track the original values when splitting an attendance
    original_check_in = fields.Datetime(tracking=True)

    original_check_out = fields.Datetime(tracking=True)

    splitted = fields.Boolean(default=False, tracking=True)

    splitted_to_attendance_id = fields.Many2one("hr.attendance", tracking=True)

    shift_type = fields.Selection(
        [
            ("", _("Unknown")),
            ("morning", _("Morning")),
            ("afternoon", _("Afternoon")),
            ("night", _("Night")),
        ],
        compute="_compute_shift_type",
        store=True,
    )

    entry_type = fields.Many2one(
        "hr.entry.type", compute="_compute_entry_type", store=True
    )

    consecutive_days = fields.Integer(
        compute="_compute_consecutive_days", store=True, default=1
    )

    extra_time = fields.Float(
        compute="_compute_entry_extra_time", store=True, default=0
    )

    extra_time_with_factor = fields.Float(
        compute="_compute_entry_extra_time_with_factor", store=True, default=0
    )

    # Computed fields methods

    @api.depends("check_in")
    def _compute_date(self):
        for record in self:
            if record.no_recompute:
                continue
            if record.check_in:
                record.date = record.check_in.date()
            else:
                record.date = False

    @api.depends("check_in")
    def _compute_is_holiday(self):
        holiday_model = self.env["hr.holidays.public"]
        for record in self:
            if record.no_recompute:
                continue
            if record.check_in:
                # Check if the check_in date is a public holiday
                record.is_holiday = holiday_model.is_public_holiday(
                    record.check_in.date()
                )
            else:
                # If there is no check_in, we can't compute if it's a holiday
                record.is_holiday = False

    @api.depends("check_in", "consecutive_days")
    def _compute_is_relevo(self):
        for record in self:
            if record.no_recompute:
                continue
            tz = timezone(record.env.user.tz or "Europe/Madrid")
            check_in = record.check_in.replace(tzinfo=timezone("UTC")).astimezone(tz)

            if record.consecutive_days == 6:
                record.is_relevo = False
                continue

            # if is holiday, is not relevo
            if record.is_holiday:
                record.is_relevo = False
                continue

            # if check_in is between Monday and Friday, is relevo
            weekday = check_in.weekday()
            if weekday < 5:
                record.is_relevo = True
                continue

            #  if check_in is in Sunday but shift_type is night, is relevo
            if check_in.weekday() == 6 and record.shift_type == "night":
                record.is_relevo = True
                continue

    @api.depends("check_out")
    def _compute_shift_type(self):
        # Get user timezone, or use Europe/Madrid as default
        tz = timezone(self.env.user.tz or "Europe/Madrid")
        for record in self:
            if record.no_recompute:
                continue
            if record.check_in and record.check_out:
                # Convert check_in and check_out to local time
                check_in = record.check_in.replace(tzinfo=timezone("UTC")).astimezone(
                    tz
                )
                check_out = record.check_out.replace(tzinfo=timezone("UTC")).astimezone(
                    tz
                )
                midpoint = check_in + (check_out - check_in) / 2
                hour = midpoint.hour
                if 5 <= hour < 13:
                    shift_type = "morning"
                elif 13 <= hour < 21:
                    shift_type = "afternoon"
                else:
                    shift_type = "night"
                record.shift_type = shift_type

    @api.depends("check_in", "is_relevo", "shift_type")
    def _compute_entry_type(self):
        for record in self:
            if record.no_recompute:
                continue

            # If employee works in the office, set the entry type to office
            if (
                record.employee_id.mother_calendar_id.id
                == self.env.ref("hr_attendance_mitxelena.office_calendar").id
            ):
                record.entry_type = self.env.ref("hr_entry_type_mitxelena.office").id
                continue

            if record.is_holiday:
                record.entry_type = self.env.ref("hr_entry_type_mitxelena.holiday").id
                continue

            if record.consecutive_days == 6:
                record.entry_type = self.env.ref("hr_entry_type_mitxelena.6th_day").id
            elif record.count_as_weekend():
                record.entry_type = self.env.ref("hr_entry_type_mitxelena.weekend").id
                if record.check_in.weekday() == 5 and record.shift_type == "morning":
                    record.entry_type = self.env.ref(
                        "hr_entry_type_mitxelena.saturday_morning"
                    ).id
            elif record.is_relevo and record.shift_type != "night":
                record.entry_type = self.env.ref("hr_entry_type_mitxelena.relevo").id
            elif record.is_relevo and record.shift_type == "night":
                record.entry_type = self.env.ref(
                    "hr_entry_type_mitxelena.relevo_night"
                ).id
            else:
                record.entry_type = "not computed"
                _logger.error("Entry type not computed for %s", record)

    @api.depends("check_in", "shift_type", "worked_hours")
    def _compute_consecutive_days(self):
        for record in self:
            if record.no_recompute:
                continue
            # If there is no check_in, set consecutive days to 0
            # and break the loop
            if not record.check_in:
                record.consecutive_days = 0
                return record.consecutive_days

            # Get the last 7 days range
            datetime_end = record.check_in
            datetime_start = datetime_end - timedelta(days=7)

            # Only select attendances where worked_hours > 0.5 hours
            # to avoid erroneous short attendances
            attendance_records = record.env["hr.attendance"].search(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("check_in", ">=", datetime_start),
                    ("check_in", "<=", datetime_end),
                    ("worked_hours", ">", 0.5),
                ],
                order="check_in desc",
            )

            # Init inner-loop variables
            previous_record = None
            consecutive_days = 1
            _logger.debug(
                "[%s][%i][Init] Counting consecutive days", record.id, consecutive_days
            )

            # If there are no attendance records, set consecutive days to 1
            # and break the loop
            if len(attendance_records) == 0:
                record.consecutive_days = 1
                _logger.debug(
                    "[%s][%i] No previous attendance records found",
                    record.id,
                    consecutive_days,
                )
                record.consecutive_days = consecutive_days

            # Iterate over the past attendance records
            for rec in attendance_records:
                _logger.debug("[%s] Checking past attendance %s", record.id, rec)

                # If there is no previous record, set it to the current one
                # and continue the loop
                if not previous_record:
                    previous_record = rec
                    _logger.debug(
                        "[%s] No previous record found, setting %s", record.id, rec
                    )
                    continue

                check_in_date = rec.check_in.date()
                previous_check_in_date = previous_record.check_in.date()

                # If the previous record it's not within the last day
                # break the loop and stop counting consecutive days
                is_consecutive = (previous_check_in_date - check_in_date) <= timedelta(
                    days=1
                )

                if not is_consecutive:
                    _logger.debug(
                        "[%s] Records are not consecutive (%s)", record.id, rec.id
                    )
                    break

                # If the previous record it is not the same day,
                # add a consecutive day and continue the loop
                if previous_check_in_date != check_in_date:
                    consecutive_days += 1
                    _logger.debug(
                        "[%s] +1 consecutive days: %i", record.id, consecutive_days
                    )
                    previous_record = rec
                    continue

                # If the previous record has less than 2 hours worked,
                # skip this record and continue the loop
                if rec.worked_hours < 2:
                    _logger.debug(
                        "[%s] Same day, but less than 2 hours worked (%s)",
                        record.id,
                        rec.id,
                    )
                    previous_record = rec
                    continue

                time_difference = previous_record.check_in - rec.check_out

                # If the previous record it's more than 7 hours
                # from the current one, add a consecutive day
                if time_difference >= timedelta(hours=7):
                    _logger.debug(
                        "[%s] Same day, but more than 7 hours difference", record.id
                    )

                    consecutive_days += 1

                    _logger.debug(
                        "[%s] so, +1 consecutive days: %i", record.id, consecutive_days
                    )

                    # Set the previous record to the current one
                    previous_record = rec

            # Set the final consecutive days count to the record
            record.consecutive_days = consecutive_days

            _logger.debug(
                "[%s][%i][Final] Consecutive days for %s has ended.",
                record.id,
                consecutive_days,
                record.employee_id.name,
            )

    @api.depends("worked_hours")
    def _compute_entry_extra_time(self):
        for record in self:
            if record.no_recompute:
                continue
            theorical_hours = record.employee_id.resource_calendar_id.hours_per_day
            extra_time = max(
                self.compute_day_extra_time(record.worked_hours, theorical_hours), 0
            )
            record.extra_time = extra_time

    @api.depends("extra_time")
    def _compute_entry_extra_time_with_factor(self):
        """ """
        for record in self:
            if record.no_recompute:
                continue
            extra_time = record.extra_time
            # Disallow negative extra time for extra_time type entries
            if extra_time < 0:
                extra_time = 0
            if record.entry_type.is_extra_time:
                extra_time = record.worked_hours
            record.extra_time_with_factor = self.compute_day_extra_time_with_factor(
                extra_time, record.entry_type.factor
            )

    # Auxiliary methods
    def count_as_weekend(self):
        # Get user timezone, or use Europe/Madrid as default
        tz = timezone(self.env.user.tz or "Europe/Madrid")
        self.ensure_one()
        check_in = self.check_in.replace(tzinfo=timezone("UTC")).astimezone(tz)
        # if is holiday, is not weekend
        if self.is_holiday:
            return False
        # if check_in is in Sunday but shift_type is night, is not weekend
        if check_in.weekday() == 6 and self.shift_type == "night":
            return False
        # if check_in is between Monday and Friday, is not weekend
        if check_in.weekday() < 5:
            return False
        return True

    # Recompute methods
    def recompute_all(self, domain=None):
        if not domain:
            domain = []
        # Get records from _context
        if self._context.get("active_ids"):
            domain.append(("id", "in", self._context.get("active_ids")))
        # Get all records  from hr.attendance and iterate over them
        attendance_records = self.env["hr.attendance"].search(domain)
        _logger.debug("Attendance records: %s", attendance_records)
        for record in attendance_records:
            if record.no_recompute:
                _logger.debug("Skipping %s as ", record)
                continue
            _logger.debug("Updating %s", record)
            record._compute_date()
            record._compute_is_holiday()
            _logger.debug("Is holiday: %s", record.is_holiday)
            record._compute_shift_type()
            _logger.debug("Shift type: %s", record.shift_type)
            record._compute_consecutive_days()
            _logger.debug("Consecutive days: %s", record.consecutive_days)
            record._compute_is_relevo()
            _logger.debug("Is relevo: %s", record.is_relevo)
            record._compute_entry_type()
            _logger.debug("Entry type: %s", record.entry_type)
            record._compute_entry_extra_time()
            _logger.debug("Extra time: %s", record.extra_time)
            _logger.debug("Extra time with factor: %s", record.extra_time_with_factor)

    def recompute_shifts(self, since=None):
        if not since:
            since = datetime.now() - timedelta(days=30)
        else:
            since = datetime.strptime(since, "%Y-%m-%d")
        tz = timezone(self.env.user.tz or "Europe/Madrid")
        attendance_records = self.env["hr.attendance"].search(
            [("check_in", ">=", since)]
        )
        _logger.debug("Attendance records: %s", attendance_records)
        for record in attendance_records:
            try:
                check_in = record.check_in.replace(tzinfo=timezone("UTC")).astimezone(
                    tz
                )
                check_out = record.check_out.replace(tzinfo=timezone("UTC")).astimezone(
                    tz
                )
                midpoint = check_in + (check_out - check_in) / 2
                hour = midpoint.hour
                if 5 <= hour < 13:
                    shift_type = "morning"
                elif 13 <= hour < 21:
                    shift_type = "afternoon"
                else:
                    shift_type = "night"
                record.shift_type = shift_type
                _logger.debug("Shift type %s for %s", shift_type, record)
                if record.shift_type != shift_type:
                    _logger.error("Shift type is %s for %s", record.shift_type, record)
                record._compute_consecutive_days()
            except Exception as e:
                _logger.error("Error computing shift type for %s: %s", record, e)

    # Helper methods
    def compute_day_extra_time(self, hours, theorical_hours):
        """
        Substract the theorical hours from the actual hours worked
        """
        extra_time = hours - theorical_hours
        return extra_time

    def compute_day_extra_time_with_factor(self, extra_time, factor):
        """
        Multiply the given extra time by the given factor
        """
        extra_time_with_factor = extra_time * factor
        return extra_time_with_factor

    def compute_compensatory_days(self, month=None):
        """
        Compute compensatory days for the given month.
        If no month is given, it will compute the last month.

        :param month: (int) Month to compute compensatory days for

        """
        today = fields.Datetime.now()
        if not month:
            last_month = today - relativedelta(months=1)
            last_month = last_month.replace(day=1)
        else:
            last_month = datetime(year=today.year, month=month, day=1)
        first_day, last_day = monthrange(last_month.year, last_month.month)
        # create a datetime object with the first and last day of the month

        first_check_in = datetime(last_month.year, last_month.month, first_day)
        last_check_in = datetime(last_month.year, last_month.month, last_day)

        attendance_records = self.env["hr.attendance"].search(
            [
                ("check_in", ">=", first_check_in),
                ("check_in", "<=", last_check_in),
                ("extra_time", ">", 0),
            ]
        )
        extra_time_by_employee = {}
        for record in attendance_records:
            if record.employee_id.id not in extra_time_by_employee.keys():
                extra_time_by_employee[record.employee_id.id] = {
                    "name": record.employee_id.name,
                    "extra_time": 0,
                    "hours_per_day": record.employee_id.resource_calendar_id.hours_per_day,
                }
            extra_time_by_employee[record.employee_id.id][
                "extra_time"
            ] += record.extra_time_with_factor

        for employee in extra_time_by_employee.keys():
            record.env["hr.leave.allocation"].create(
                {
                    "name": "Compensatory days for %s" % last_month.strftime("%B %Y"),
                    "employee_id": employee,
                    "holiday_status_id": record.env.ref(
                        "hr_holidays.holiday_status_comp"
                    ).id,
                    "number_of_days": extra_time_by_employee[employee]["extra_time"]
                    / extra_time_by_employee[employee]["hours_per_day"],
                }
            )

            _logger.debug(
                "Compensatory hours for %s: %s",
                extra_time_by_employee[employee]["name"],
                extra_time_by_employee[employee]["extra_time"],
            )

    def get_day_worked_time(self):
        """
        Get the total worked time in the last ATTENDANCE_WINDOW hours
        (default 12 hours)
        """
        day_worked_time = self.env["hr.attendance"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                (
                    "check_out",
                    ">=",
                    self.check_in - timedelta(hours=self.get_attendance_window()),
                ),
                ("check_in", "<=", self.check_in),
            ]
        )
        worked_hours = sum(day_worked_time.mapped("worked_hours"))
        return worked_hours

    def get_day_extra_time(self):
        """
        Get the total extra time in the last ATTENDANCE_WINDOW hours
        If there is no extra time, return 0
        """
        worked_hours = self.get_day_worked_time()
        day_extra_time = self.compute_day_extra_time(
            worked_hours, self.employee_id.resource_calendar_id.hours_per_day
        )
        return max(day_extra_time, 0)

    def process_attendance_overtime(self, force_recompute=False):
        """Process the attendance to split it into regular hours and overtime for completed records."""

        # If no_recompute is set or there is no check_out, skip the record
        if (self.no_recompute or not self.check_out) and not force_recompute:
            return

        # If the entry type is extra time, set the extra time to the worked hours
        if self.entry_type.is_extra_time:
            updated_entry = self.write(
                {
                    "is_overtime": True,
                    "is_overtime_due": True,
                    "no_recompute": True,
                    "time_changed_manually": False,
                    "extra_time": self.worked_hours,
                }
            )
            return

        # Get the last attendance record
        previous_attendance = self.env["hr.attendance"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("check_out", "<=", self.check_in),
            ],
            limit=1,
            order="check_out desc",
        )

        dt_original_check_out = fields.Datetime.from_string(self.check_out)
        dt_original_check_in = fields.Datetime.from_string(self.check_in)
        attendance_window = dt_original_check_out - timedelta(
            hours=self.get_attendance_window()
        )

        # If the last attendance record is overtime and the check_out is
        # within the attendance window, inherit the entry type and shift type
        # from the last attendance record

        if (
            previous_attendance
            and previous_attendance.is_overtime
            and previous_attendance.check_out >= attendance_window
        ):
            original_entry = self.read()[0]
            self.write(
                {
                    "entry_type": previous_attendance.entry_type.id,
                    "shift_type": previous_attendance.shift_type,
                    "is_relevo": previous_attendance.is_relevo,
                    "is_overtime": True,
                    "is_overtime_due": True,
                    "no_recompute": True,
                    "consecutive_days": previous_attendance.consecutive_days,
                    "time_changed_manually": False,
                    "extra_time": self.worked_hours,
                    "extra_time_with_factor": self.compute_day_extra_time_with_factor(
                        self.worked_hours, previous_attendance.entry_type.factor
                    ),
                }
            )

            self._post_message_with_attendance_link(previous_attendance.id, "update")
            body = _(
                f"Original values for entry: <ul><li><strong>Extra time:</strong> {original_entry['extra_time']}</li> <li><strong>Extra time with factor:</strong> {original_entry['extra_time_with_factor']}</li></ul>"
            )
            self.message_post(body=body)
            return

        # Get day worked and extra hours
        worked_hours = self.get_day_worked_time()
        day_extra_time = self.compute_day_extra_time(
            worked_hours, self.employee_id.resource_calendar_id.hours_per_day
        )

        # If there is no extra time, leave the entry type as it is
        if day_extra_time <= 0:
            return
        # TODO : if day_extra_time > self.worked_hours:
        # If there is extra time, set the check_out to the expected check_out time
        new_checkout = dt_original_check_out - timedelta(hours=day_extra_time)
        if new_checkout <= self.check_in:
            # This must be a pre-computed attendance record
            return
        original_entry = self.read()[0]
        self.write(
            {
                "check_out": new_checkout,
                "no_recompute": True,
                "extra_time": 0,
                "extra_time_with_factor": 0,
                "time_changed_manually": False,
                "original_check_in": dt_original_check_in,
                "original_check_out": dt_original_check_out,
                "splitted": True,
            }
        )

        # And create a new attendance record with the extra time
        new_entry = self.env["hr.attendance"].create(
            {
                "employee_id": self.employee_id.id,
                "check_in": new_checkout,
                "check_out": dt_original_check_out,
                "is_overtime": True,
                "is_overtime_due": True,
                "no_recompute": True,
                "shift_type": self.shift_type,
                "is_relevo": self.is_relevo,
                "entry_type": self.entry_type.id,
                "extra_time": day_extra_time,
                "consecutive_days": self.consecutive_days,
                "extra_time_with_factor": self.compute_day_extra_time_with_factor(
                    day_extra_time, self.entry_type.factor
                ),
                "time_changed_manually": False,
                "original_check_in": dt_original_check_in,
                "original_check_out": dt_original_check_out,
                "splitted": True,
                "splitted_to_attendance_id": self.id,
                "date": self.date,
            }
        )

        self.post_split_attendance_message(new_entry, original_entry)

    def undo_split_attendance(self):
        """Merge the overtime attendance record with the original one"""
        if not self.splitted_to_attendance_id:
            return
        original_attendance = self.splitted_to_attendance_id
        original_check_out = fields.Datetime.from_string(self.check_out)
        self.unlink()
        splitted_id = original_attendance.id
        original_attendance.write(
            {
                "check_out": original_check_out,
                "no_recompute": False,
                "extra_time": 0,
                "extra_time_with_factor": 0,
                "time_changed_manually": False,
                "original_check_in": False,
                "original_check_out": False,
                "splitted": False,
            }
        )
        original_attendance._post_message_with_attendance_link(splitted_id, "undo")

    def action_undo_split_attendance(self):
        for record in self:
            record.undo_split_attendance()

    def action_process_attendance_overtime(self, force_recompute=False):
        records = self.sorted(key=lambda r: r.check_in)
        for record in records:
            record.process_attendance_overtime(force_recompute)

    def _post_message_with_attendance_link(self, attendance_id, type="from"):
        from_text = _("From attendance: ")
        new_text = _("New attendance: ")
        msg = from_text
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if type != "from":
            msg = new_text
        elif type == "update":
            msg = _(
                "Updated entry: Inheriting values as previous attendance record was already overtime: "
            )
        elif type == "undo":
            msg = _("Split undone: ")
        message = (
            msg
            + "<a href='{}/web#id={}&model=hr.attendance&view_type=form'>#{}</a>".format(
                base_url, attendance_id, attendance_id
            )
        )
        self.message_post(
            body=message, subject="_(Attendance split)", subtype_xmlid="mail.mt_note"
        )

    def post_split_attendance_message(self, new_entry, original_entry):
        subtype = "mail.mt_note"
        company_tz = self.env.user.tz or "UTC"
        original_check_in = (
            fields.Datetime.from_string(original_entry["check_in"])
            .replace(tzinfo=utc)
            .astimezone(timezone(company_tz))
        )
        original_check_out = (
            fields.Datetime.from_string(original_entry["check_out"])
            .replace(tzinfo=utc)
            .astimezone(timezone(company_tz))
        )
        formated_check_in = original_check_in.strftime("%d/%m/%Y %H:%M:%S")
        formated_check_out = original_check_out.strftime("%d/%m/%Y %H:%M:%S")
        body = f"Original values for entry:<br> <ul><li><strong>Check_in:</strong> {formated_check_in}</li> <li><strong>Check_out:</strong> {formated_check_out}</li></ul>"
        self._post_message_with_attendance_link(new_entry.id, "new")
        self.message_post(
            body=body, subject="_(Attendance split log)", subtype_xmlid=subtype
        )
        new_entry._post_message_with_attendance_link(self.id)
        new_entry.message_post(
            body=body, subject="_(Attendance split log)", subtype_xmlid=subtype
        )

    def action_update_extra_time(self):
        for record in self:
            if record.is_overtime and record.extra_time < record.worked_hours:
                record.extra_time = record.worked_hours
                record.extra_time_with_factor = self.compute_day_extra_time_with_factor(
                    record.worked_hours, record.entry_type.factor
                )
