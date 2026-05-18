from odoo import models, fields


class GymPackage(models.Model):
    _name = 'gym.package'
    _description = 'Gym Membership Package' # تعريف موديل باقات الاشتراك في الجيم(شهر - 3 شهور - سنة)

    name = fields.Char(string="Package Name", required=True)
    duration_days = fields.Integer(string="Duration (Days)", required=True)
    price = fields.Float(string="Price", required=True)
    description = fields.Text(string="Description")
