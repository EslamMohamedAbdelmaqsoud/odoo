from odoo import models, fields, api
from odoo.exceptions import ValidationError


# TransientModel is used for temporary data storage, such as wizards. It does not create a permanent table in the database.
class ExWizard(models.TransientModel):
    _name = 'ex.wizard'  # Model name for table database
    _description = 'Student Enrollment Wizard'

    # Fields for the wizard
    student_id = fields.Many2one('student', string='Student', required=True,
                                 help='Select a student to enroll')
    course_id = fields.Many2one('course', string='Course', required=True,
                                help='Select a course to enroll the student in')
    class_id = fields.Many2one('classs', string='Class', required=True,
                               help='Select a class for the student')
    enrollment_date = fields.Date(string='Enrollment Date', required=True,
                                  default=fields.Date.today,
                                  help='Date when the student will be enrolled')
    notes = fields.Text(string='Notes', help='Additional notes about the enrollment')

    # Action method to confirm enrollment
    def action_enroll(self):
        """
        This method handles the enrollment of a student into a course and class.
        """
        for wizard in self:
            # Validate student is active
            if not wizard.student_id.active:
                raise ValidationError(f"Cannot enroll inactive student: {wizard.student_id.name}")

            # Validate class belongs to the correct year
            if wizard.class_id.year_id:
                # Check if student already has a year assigned
                if wizard.student_id.year_id and wizard.student_id.year_id != wizard.class_id.year_id:
                    raise ValidationError(
                        f"Student {wizard.student_id.name} is already enrolled in year "
                        f"{wizard.student_id.year_id.name}"
                    )

            # Update student with course and class
            wizard.student_id.write({
                'course_id': wizard.course_id.id,
                'class_id': wizard.class_id.id,
                'enrollment_date': wizard.enrollment_date,
                'state': 'pending',
            })

            # Log activity
            wizard.student_id.message_post(
                body=f"Student enrolled in course <b>{wizard.course_id.name}</b> "
                     f"and class <b>{wizard.class_id.name}</b><br/>"
                     f"Enrollment Date: <b>{wizard.enrollment_date}</b><br/>"
                     f"Notes: {wizard.notes if wizard.notes else 'None'}",
                subject="Student Enrolled"
            )

        return {'type': 'ir.actions.act_window_close'}


