from odoo import models, fields


class Classs(models.Model):
    _name = 'classs'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities


    name = fields.Char(string="Class Name",required=True,tracking=True)
    description = fields.Char(string="Description")
    year_id = fields.Many2one('year', string='Year')
