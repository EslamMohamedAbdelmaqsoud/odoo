from odoo import models, fields


class SchoolCustomer(models.Model):
    _name = 'school.customer'
    _description = 'School Customer'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    name = fields.Char(string='Name', required=True, tracking=True)
    phone = fields.Char(string='Phone', required=1, size=11, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    address = fields.Text(string='Address', tracking=True)
    active = fields.Boolean(string='Active', default=True)

    # Smart button to show the number of orders related to this customer
    order_count = fields.Integer(string='Order Count', compute='_compute_order_count', store=True)

    def _compute_order_count(self):
        for rec in self:
            rec.order_count = self.env['school.order'].search_count([('customer_id', '=', rec.id)])

    def action_view_orders(self):
        self.ensure_one()
        return {
            'name': 'Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'school.order',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id},
        }
