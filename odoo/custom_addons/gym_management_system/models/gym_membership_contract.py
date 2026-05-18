from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError


class GymMembership(models.Model):
    _name = 'gym.membership'
    _description = 'Gym Membership Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # لإضافة الشات في الأسفل

    member_id = fields.Many2one('res.partner', string="Member", required=True, domain=[('is_gym_member', '=', True)])
    package_id = fields.Many2one('gym.package', string="Package", required=True)

    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, required=True)
    end_date = fields.Date(string="End Date", compute="_compute_end_date", store=True, readonly=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('frozen', 'Frozen')
    ], string="Status", default='draft', tracking=True)

    @api.depends('start_date', 'package_id')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date and rec.package_id:
                # إضافة أيام الباقة إلى تاريخ البداية
                rec.end_date = rec.start_date + timedelta(days=rec.package_id.duration_days)
            else:
                rec.end_date = False

        # إضافة حقل لربط الاشتراك بالفاتورة التي ستنشأ عند تأكيد الاشتراك
    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)

    def action_confirm(self):
        for rec in self:
            if not rec.member_id.email:
                raise UserError(_("Please set an email for the member before confirming."))

            # 1. تغيير حالة الاشتراك
            rec.state = 'active'
            rec.member_id.membership_status = 'active'

            # 2. إنشاء الفاتورة تلقائياً
            invoice_vals = {
                'move_type': 'out_invoice',  # نوع المستند: فاتورة عميل
                'partner_id': rec.member_id.id,
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': [(0, 0, {
                    'name': f"Membership Subscription: {rec.package_id.name}",
                    'quantity': 1,
                    'price_unit': rec.package_id.price,
                })],
            }
            invoice = self.env['account.move'].create(invoice_vals)
            rec.invoice_id = invoice.id

        return True

        # دالة لفتح الفاتورة من داخل الاشتراك (Smart Button Logic)

    def action_view_invoice(self):
        return {
            'name': _('Membership Invoice'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'type': 'ir.actions.act_window',
        }

    # Cron job to check for expired memberships
    @api.model
    def _check_membership_expiry(self):
        """تُستدعى هذه الدالة بواسطة Scheduled Action"""
        today = fields.Date.context_today(self)
        expired_memberships = self.search([
            ('state', '=', 'active'),
            ('end_date', '<', today)
        ])
        for membership in expired_memberships:
            membership.state = 'expired'
            membership.member_id.membership_status = 'expired'
