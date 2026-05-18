from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolOrder(models.Model):
    _name = 'school.order'
    _description = 'School Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    name = fields.Char(string='Order Number', required=True, readonly=True, copy=False, default='New')
    customer_id = fields.Many2one('school.customer', string='Customer', required=True)
    order_date = fields.Date(string='Order Date', default=fields.Date.context_today, tracking=True)
    order_line_ids = fields.One2many('school.order.line', 'order_id', string='Order Lines')
    total_order = fields.Float(string='Total Order', compute='_compute_total_order', store=True)

    # Status Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', readonly=True, tracking=True)

    ########################### Create method to generate reference number for each student using sequences ( to override the create method )
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('school.order') or 'New'
        return super(SchoolOrder, self).create(vals)

    ####################### Computed Method Field: ( total order ) ########################
    @api.depends('order_line_ids.subtotal')
    def _compute_total_order(self):
        for order in self:
            order.total_order = sum(rec.subtotal for rec in order.order_line_ids)

    def action_confirm_order(self):
        for order in self:
            if not order.order_line_ids:
                raise ValidationError("You cannot confirm an empty order.")

            for line in order.order_line_ids:
                if line.product_id.quantity < line.quantity:
                    raise ValidationError(
                        f"Insufficient stock for product '{line.product_id.name}'. "
                        f"Available: {line.product_id.quantity}, Required: {line.quantity}."
                    )
                line.product_id.quantity -= int(line.quantity)
            order.state = 'confirmed'

    def action_cancel_order(self):
        for order in self:
            if order.state == 'confirmed':
                for line in order.order_line_ids:
                    line.product_id.quantity += int(line.quantity)
            order.state = 'cancelled'


class SchoolOrderLine(models.Model):
    _name = 'school.order.line'
    _description = 'School Order Line'

    product_id = fields.Many2one('school.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    price = fields.Float(string='Price', required=True, related='product_id.price')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    order_id = fields.Many2one('school.order', string='Order', ondelete='cascade')

    ####################### Computed Method Field: ( subtotal ) ########################
    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.price
