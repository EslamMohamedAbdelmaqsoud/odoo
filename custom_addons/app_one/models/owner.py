from odoo import models, fields


class Owner(models.Model):
    _name = 'owner'

    name = fields.Char(required=1, default='New Owner')
    phone = fields.Char(required=1, size=11)
    email = fields.Char(required=1, )
    description = fields.Text()
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female')
    ])
    property_ids = fields.One2many('property', 'owner_id')
