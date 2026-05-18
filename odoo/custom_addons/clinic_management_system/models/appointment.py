from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Appointment(models.Model):
    _name = 'appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    patient_id = fields.Many2one('patient', string="Patient", required=True)
    appointment_time = fields.Datetime(string="Appointment Time", default=fields.Datetime.now)
    doctor_id = fields.Many2one('res.users', string="Doctor", required=True)  # سنستخدم مستخدمي النظام كأطباء حالياً
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string="Status", default='draft', tracking=True)
    prescription = fields.Html(string="Prescription")

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'

    from odoo.exceptions import ValidationError

    @api.constrains('appointment_time')
    def _check_date_validity(self):
        for rec in self:
            if rec.appointment_time and rec.appointment_time < fields.Datetime.now():
                raise ValidationError("لا يمكن حجز موعد في وقت سابق!")

    @api.constrains('patient_id')
    def _check_unique_patient_appointment(self):
        for rec in self:
            # منع حجز أكثر من موعد "مسودة" لنفس المريض
            search_count = self.env['appointment'].search_count([
                ('patient_id', '=', rec.patient_id.id),
                ('state', '=', 'draft'),
                ('id', '!=', rec.id)
            ])
            if search_count > 0:
                raise ValidationError("هذا المريض لديه موعد معلق بالفعل!")

    # وظيفة مجدولة لإلغاء المواعيد المنتهية التي لم يتم تأكيدها
    @api.model
    def cron_cancel_expired_appointments(self):
        # البحث عن المواعيد التي لم يتم تأكيدها ومر وقتها
        expired = self.search([
            ('state', '=', 'draft'),
            ('appointment_time', '<', fields.Datetime.now())
        ])
        if expired:
            expired.write({'state': 'cancel'})
            for rec in expired:
                rec.message_post(body="تم إلغاء الموعد تلقائياً بواسطة النظام لانتهاء الوقت.")

    def action_confirm(self):
        self.state = 'confirmed'
        template = self.env.ref('clinic_management_system.email_template_appointment_confirmation')
        for rec in self:
            if rec.patient_id.email:
                template.send_mail(rec.id, force_send=True)
