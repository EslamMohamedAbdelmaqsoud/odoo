from odoo import models, fields


class Year(models.Model):
    _name = 'year'
    _rec_name = 'number'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    number = fields.Integer(string='Year Number', required=True, tracking=True)
    class_ids = fields.One2many('classs', 'year_id', string='Classes')
