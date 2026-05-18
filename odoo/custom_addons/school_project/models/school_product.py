from odoo import models, fields


class SchoolProduct(models.Model):
    _name = 'school.product'
    _description = 'School Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    name = fields.Char(string='Name', required=True, tracking=True)
    price = fields.Float(string='Price', required=True, tracking=True)
    quantity = fields.Integer(string='Quantity', required=True, tracking=True)
    available = fields.Boolean(string='Available', default=True, tracking=True)
