from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ref = fields.Char(string="Customer Reference", default='New')  # to generate a reference number for each property ( Add Sequences )

    credit = fields.Float(related='partner_id.credit_limit', string="Customer Credit")

    edit_2026 = fields.Char(string="Edit 2026")

    ########################### Create method to generate reference number for each Sale Order using sequences ( to override the create method )
    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('sale_order_sequence')
        return res

    # Add a new field to link the sale order to a property ( 1- Extension Model  )
    property_id = fields.Many2one('property')

    # Override the action_confirm method to add custom behavior when confirming a sale order ( Python Inheritance: 2- Method Overriding )
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        print("Sale order confirmed!")
        return res
