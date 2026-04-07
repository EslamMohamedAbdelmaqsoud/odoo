from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add a new field to link the sale order to a property ( Traditional Inheritance: 1- Extension Model  )
    property_id = fields.Many2one('property')

    # Override the action_confirm method to add custom behavior when confirming a sale order ( Python Inheritance: 2- Method Overriding )
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        print("Sale order confirmed!")
        return res
