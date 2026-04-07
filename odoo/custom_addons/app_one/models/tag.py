from odoo import models, fields


class Tag(models.Model):
    _name = 'tag'

    name = fields.Char(required=1, default='New Tag')
    description = fields.Char(string='Description')
