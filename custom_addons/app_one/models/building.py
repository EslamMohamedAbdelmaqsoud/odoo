from odoo import models, fields


class Building(models.Model):
    _name = 'building'
    _description = 'Building'  # to define the name of the model in the database
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities
    # _rec_name = 'code'  # to set the field that will be used as the record name = display name

    number = fields.Integer(string='Number')
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=True)  # to make the record active or inactive ( Features Archiving )
