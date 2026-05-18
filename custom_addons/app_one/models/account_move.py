from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'  # Inherit from the existing account.move model

    def action_do_something(self):
        print(self, "Hello from the inherited account.move model!")
