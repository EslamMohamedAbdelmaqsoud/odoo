from odoo import models


class Client(models.Model):
    _name = 'client'
    _inherit = 'owner'

    # Add a new field to link the sale order to a property ( Traditional Inheritance: 2-Inherit Models   )
