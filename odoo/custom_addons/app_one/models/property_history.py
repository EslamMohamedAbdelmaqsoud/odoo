from odoo import models, fields


class PropertyHistory(models.Model):
    _name = 'property.history'
    _description = 'Property History'  # to define the name of the model in the database

    user_id = fields.Many2one('res.users')
    property_id = fields.Many2one('property')
    old_state = fields.Char()
    new_state = fields.Char()
    reason = fields.Char()
    line_ids = fields.One2many('property.history.line', 'history_id')


# Adding Line
class PropertyHistoryLine(models.Model):
    _name = 'property.history.line'
    _description = 'Property History Line'  # to define the name of the model in the database

    history_id = fields.Many2one('property.history')
    area = fields.Float()
    description = fields.Char()
