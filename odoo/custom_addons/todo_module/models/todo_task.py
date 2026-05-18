from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'To-Do Task'  # to add description in the form view header
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    ref = fields.Char(default='New', readonly=1)  # to generate a reference number for each property ( Add Sequences )
    name = fields.Char(string="Name", required=True, default='new task', tracking=True,translate=True)
    assign_to = fields.Many2one('res.partner', string="Assign To")
    description = fields.Text(required=True, tracking=True)
    due_date = fields.Date(string='Due Date', required=True, tracking=True)
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ], default='new', tracking=True)
    estimated_time = fields.Integer(string="Estimated Time (hrs)", required=True, tracking=True)
    total_time = fields.Float(string="Total Time", compute='compute_total_time', store=True)
    line_ids = fields.One2many("todo.lines", "task_id")
    active = fields.Boolean(string='Active',
                            default=True)  # to make the record active or inactive ( Features Archiving )
    is_late = fields.Boolean()

    # Validation ( data base ) SQL Constraints
    _sql_constraints = [('unique_name', 'unique(name)', 'The name is Exist!'),
                        ]

    # to calculate Time in every line and display result in the total_time in the report
    @api.depends('line_ids.time')
    def compute_total_time(self):
        for rec in self:
            rec.total_time = sum(line.time for line in rec.line_ids)

    # to check if total time ( time in every line ) is greater than estimated_time
    @api.constrains('line_ids', 'estimated_time')
    def time_validation(self):
        for rec in self:
            total_time = sum(line.time for line in rec.line_ids)
            if total_time > rec.estimated_time:
                raise ValidationError(
                    f"The Total Time {total_time} is greater than the Estimated Time {rec.estimated_time}"
                )

    ######################### Work Flow Action Buttons ############################
    def action_new(self):
        for rec in self:
            rec.status = 'new'

    #####################################################
    def action_in_progress(self):
        for rec in self:
            rec.status = 'in_progress'

    #####################################################
    def action_completed(self):
        for rec in self:
            rec.status = 'completed'

    ####################### Server action ##############################
    def action_closed(self):
        for rec in self:
            rec.status = 'closed'

        ######################### Automated action ###################################################

    def check_due_date(self):
        tasks_ids = self.search([])
        for rec in tasks_ids:
            if rec.due_date and rec.due_date < fields.date.today() and (
                    rec.status == 'new' or rec.status == 'in_progress'):
                rec.is_late = True
            else:
                rec.is_late = False

    ########################### Create method to generate reference number for each property using sequences ( to override the create method )

    @api.model
    def create(self, vals):
        res = super(TodoTask, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('todo_task_sequence')
        return res

    ########################### Task Update Restriction ############################
    def write(self, vals):
        """
        Override write method to prevent updates on completed or closed tasks.
        This ensures data integrity by preventing modifications to finished tasks.
        However, status changes are allowed to permit reverting to earlier states.
        """
        for rec in self:
            # Check if the task is in a completed or closed state
            if rec.status in ('completed', 'closed'):
                # Allow status changes to revert to earlier states
                # Block all other field modifications
                if len(vals) > 1 or 'status' not in vals:
                    raise ValidationError(
                        f"Cannot update task '{rec.name}' with status '{rec.status}'. "
                        "Tasks marked as 'Completed' or 'Closed' are locked and cannot be modified. "
                        "To make changes, please revert the task to an earlier status."
                    )

        return super(TodoTask, self).write(vals)


class TodoLines(models.Model):
    _name = "todo.lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    num = fields.Integer(string="ID", required=True, tracking=True)
    date = fields.Date(string="Date", required=True, tracking=True)
    description = fields.Char(string="Description", tracking=True)
    time = fields.Float(string="Time (hrs)", required=True, tracking=True)
    task_id = fields.Many2one("todo.task", string="Task")
