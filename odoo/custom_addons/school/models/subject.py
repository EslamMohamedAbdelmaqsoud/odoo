from odoo import models, fields


class Subject(models.Model):
    _name = 'subject'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    name = fields.Char(string="Subject Name", required=True,tracking=True)
    description = fields.Char(string="Description", tracking=True, required=True)
    year_id = fields.Many2one('year', string="Academic Year")
    student_id = fields.Many2one('student', string="Student")