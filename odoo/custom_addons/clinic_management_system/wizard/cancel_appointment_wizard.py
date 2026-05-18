from odoo import models, fields, api

class CancelAppointmentWizard(models.TransientModel):
    _name = 'cancel.appointment.wizard'
    _description = 'Cancel Appointment Wizard'

    appointment_id = fields.Many2one('appointment', string="Appointment", readonly=True)
    reason = fields.Text(string="Reason for Cancellation", required=True)

    def action_cancel_appointment(self):
        # تحديث حالة الموعد وإضافة السبب في سجل الملاحظات (Chatter)
        self.appointment_id.state = 'cancel'
        self.appointment_id.message_post(body=f"Appointment cancelled. Reason: {self.reason}")