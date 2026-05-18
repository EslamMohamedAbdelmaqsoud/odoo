from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields

class TestClinic(TransactionCase):

    def setUp(self):
        """ إعداد البيانات الأساسية للاختبار """
        super(TestClinic, self).setUp()
        # إنشاء مريض تجريبي
        self.patient = self.env['patient'].create({
            'name': 'Test Patient',
            'phone': '123456789'
        })

    def test_01_appointment_backdating(self):
        """ اختبار: هل النظام يمنع حجز موعد بتاريخ قديم؟ """
        with self.assertRaises(ValidationError):
            self.env['appointment'].create({
                'patient_id': self.patient.id,
                'appointment_time': '2020-01-01 10:00:00',
            })

    def test_02_sequence_generation(self):
        """ اختبار: هل رقم المريض (Reference) يتم توليده تلقائياً؟ """
        patient_new = self.env['patient'].create({
            'name': 'Second Patient',
            'phone': '987654321'
        })
        self.assertNotEqual(patient_new.reference, 'New')
        self.assertTrue(patient_new.reference.startswith('PAT-'))