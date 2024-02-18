from odoo import models, fields, api


class HrAttendanceValidationSheet(models.AbstractModel):
    _name = "report.hr_attendance_mitxelena.hr_attendance_validation_sheet"

    @api.model
    def _get_report_values(self, docids, data=None):
        # Retrieve the data from the model HrAttendanceValidationSheet
        records = self.env["hr.attendance.validation.sheet"].browse(docids)

        for record in records:
            record._compute_sorted_attendance_ids()

        report_data = {
            "records": records,
        }

        return report_data
