from odoo import models, fields, api


class Course(models.Model):
    _name = 'course'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    name = fields.Char(required=1, default='New Course', tracking=True)
    price = fields.Float(required=True, tracking=True)
    discount = fields.Float(tracking=True)
    final_price = fields.Float(compute='_compute_final_price', store=True)
    description = fields.Text()
    student_ids = fields.One2many('student', 'course_id')
    line_ids = fields.One2many('course.line', 'course_id')
    active = fields.Boolean(string='Active',
                            default=True)  # to make the record active or inactive ( Features Archiving )

    ####################### Computed Method Field: ( final_price) ########################
    @api.depends('price', 'discount')
    def _compute_final_price(self):
        for rec in self:
            rec.final_price = rec.price - rec.discount

    ######################### Onchange Method ######################
    @api.onchange('price')
    def _onchange_price(self):
        for rec in self:
            if rec.price < 2000:
                return {
                    'warning': {
                        'title': 'Low Price',
                        'message': 'The price is too low, please consider increasing it.',
                        'type': 'notification',
                    }
                }
        return None


# Adding Lines
class CourseLine(models.Model):
    _name = 'course.line'

    number = fields.Integer('Room Number')
    area = fields.Float()
    description = fields.Char()
    course_id = fields.Many2one('course')
