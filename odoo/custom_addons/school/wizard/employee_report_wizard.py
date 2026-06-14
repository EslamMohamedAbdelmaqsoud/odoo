from datetime import timedelta
from odoo import models, fields


class EmployeeReportWizard(models.TransientModel):
    _name = 'employee.report.wizard'
    _description = 'HR Employee Hire Date Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    def action_print_employee_report(self):
        self.ensure_one()
        start_dt = fields.Datetime.to_datetime(self.start_date)
        end_dt = fields.Datetime.to_datetime(self.end_date) + timedelta(days=1)
        employees = self.env['hr.employee'].search([
            ('create_date', '>=', start_dt),
            ('create_date', '<', end_dt),
        ])

        data = {
            'form': self.read()[0],
            'employee_ids': employees.ids,
        }

        return self.env.ref('school.action_report_hr_employees').report_action(self, data=data)
