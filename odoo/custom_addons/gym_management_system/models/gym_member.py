from odoo import models, fields, api


class GymMember(models.Model):
    _inherit = 'res.partner'  # وراثة موديل العملاء الأساسي
    _description = 'Gym Member'  # تعريف موديل المشتركين في الجيم

    is_gym_member = fields.Boolean(string="Is Gym Member", default=True)
    member_id = fields.Char(string="Member ID", readonly=True, copy=False)
    birth_date = fields.Date(string="Birth Date")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender")
    blood_type = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'), ('o+', 'O+'), ('o-', 'O-')
    ], string="Blood Type")

    # حقل محسوب لعرض حالة الاشتراك الحالي
    membership_status = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('frozen', 'Frozen')
    ], string="Membership Status", default='expired')

    @api.model
    def create(self, vals):
        # توليد رقم تسلسلي للمشترك تلقائياً
        if not vals.get('member_id'):
            vals['member_id'] = self.env['ir.sequence'].next_by_code('gym.member.sequence')
        return super(GymMember, self).create(vals)
