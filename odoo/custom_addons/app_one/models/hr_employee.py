from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(string='Age', compute='_compute_age')

    ####################### Computed Method Field: ( age ) ########################
    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = fields.Date.today()
                age = today.year - rec.birth_date.year
                if (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day):
                    age -= 1
                rec.age = age
            else:
                rec.age = 0

    ############################ Onchange ##############################
    @api.onchange('age')
    def _onchange_check_age(self):
        for rec in self:
            if rec.age < 18:
                return {
                    'warning': {
                        'title': 'Low Age',
                        'message': 'The age is below the legal working age. Please ensure compliance with labor laws.',
                        'type': 'notification',
                    }
                }
        return None
