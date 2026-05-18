from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'  # Inherit from the existing account.move model

    # Custom fields
    custom_notes = fields.Text(string="Notes 2026")
    cost_center = fields.Char(string="Cost Center")
    internal_reference = fields.Char(string="Internal Reference")
    department = fields.Char(string="Department")

    def action_do_something(self):
        print(self, "Hello from the inherited account.move model!")
