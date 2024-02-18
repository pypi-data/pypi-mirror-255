from odoo import fields, models, _


class AllocationModificationWizard(models.TransientModel):
    _name = "hr.leave.allocation.modification.wizard"
    _description = "Allocation Modification Wizard"

    employee_id = fields.Many2one("hr.employee", string="Employee", readonly=True)

    substraction = fields.Boolean(string="Substraction", default=True)
    hours = fields.Float(string="Hours", default=0.0)
    comment = fields.Text(string="Comment", default=_("Paid leave modification"))

    def modify_allocation(self):
        allocation_id = self.env["hr.leave.allocation"].browse(
            self.env.context.get("active_id")
        )
        if self.substraction:
            allocation_id.write(
                {
                    "number_of_days": allocation_id.number_of_days
                    - self.hours / allocation_id.employee_id.resource_calendar_id.hours_per_day,
                }
            )
        else:
            allocation_id.write(
                {
                    "number_of_days": allocation_id.number_of_days
                    + self.hours / allocation_id.employee_id.resource_calendar_id.hours_per_day
                }
            )
        allocation_id.message_post(body=self.comment)
        return {"type": "ir.actions.act_window_close"}