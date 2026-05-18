from odoo import models, fields, api
from datetime import date


class Patient(models.Model):
    _name = 'patient'
    _description = 'Patient Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Adding Chatter

    name = fields.Char(string='Name', required=True, tracking=True)
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, default='New')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    phone = fields.Char(string="Phone", tracking=True, size=11)
    email = fields.Char(string="Email")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_patient_phone', 'unique(phone)', 'رقم الهاتف مسجل لمريض آخر مسبقاً!'),
        ('unique_patient_email', 'unique(email)', 'البريد الإلكتروني مستخدم بالفعل!')
    ]


    # حساب العمر بناءً على تاريخ الميلاد
    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                rec.age = date.today().year - rec.date_of_birth.year
            else:
                rec.age = 0

    # Override the create method to set the reference field using a sequence
    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('patient') or 'New'
        return super(Patient, self).create(vals)

    appointment_count = fields.Integer(string="Appointment Count", compute="_compute_appointment_count")

    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['appointment'].search_count([('patient_id', '=', rec.id)])

    def action_view_appointments(self):
        return {
            'name': 'Appointments',
            'res_model': 'appointment',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }
