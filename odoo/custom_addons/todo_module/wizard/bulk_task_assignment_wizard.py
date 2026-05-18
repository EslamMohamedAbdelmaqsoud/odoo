from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BulkTaskAssignmentWizard(models.TransientModel):
    _name = 'bulk.task.assignment.wizard'
    _description = 'Bulk Task Assignment Wizard'

    employee_id = fields.Many2one('res.partner', string='Assign To Employee', required=True)
    task_ids = fields.Many2many('todo.task', string='Select Tasks', required=True)
    description = fields.Text(string='Assignment Description', help='Optional: Add notes about the assignment')

    @api.model
    def default_get(self, fields_list):
        """
        Pre-populate the wizard with selected tasks from the context
        """
        res = super().default_get(fields_list)

        # Get active IDs from context (selected tasks in the list view)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['task_ids'] = [(6, 0, active_ids)]

        return res

    def action_assign_tasks(self):
        """
        Assign selected tasks to the chosen employee
        """
        if not self.task_ids:
            raise ValidationError('Please select at least one task to assign.')

        if not self.employee_id:
            raise ValidationError('Please select an employee to assign tasks to.')

        # Assign all selected tasks to the employee
        for task in self.task_ids:
            task.assign_to = self.employee_id

        # Return success notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': 'Tasks Assigned Successfully',
                'message': f'{len(self.task_ids)} task(s) have been assigned to {self.employee_id.name}',
                'sticky': False,
            }
        }

