from odoo import models, api


class EmployeeReportAbstract(models.AbstractModel):
    _name = 'report.school.report_employee_hire_template'
    _description = 'HR Employee Report Data Logic'

    @api.model
    def _get_report_values(self, docids, data=None):
        employee_ids = data.get('employee_ids', [])
        docs = self.env['hr.employee'].browse(employee_ids)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': docs,
            'start_date': data['form'].get('start_date'),
            'end_date': data['form'].get('end_date'),
        }
