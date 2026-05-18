from odoo import models, fields


# TransientModel is used for temporary data storage, such as wizards. It does not create a permanent table in the database.
class ChangeStateWizard(models.TransientModel):
    _name = 'change.state.wizard'  # Model name for table database
    _description = 'Change State Wizard'

    property_id = fields.Many2one('property')  # Many2one field to select a property
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
    ], default='draft')
    reason = fields.Char()

    def action_confirm(self):
        if self.property_id.state == 'closed':
            self.property_id.state = self.state  # Update the state of the selected property
            self.property_id.create_history_record('closed', self.state, self.reason)
