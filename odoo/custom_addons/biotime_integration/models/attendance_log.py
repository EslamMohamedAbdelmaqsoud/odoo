import requests
import pytz
from datetime import datetime
from odoo import models, fields, api, _


class BioTimeRawLog(models.Model):
    _name = 'biotime.raw.log'
    _description = 'جدول حركات البصمة الخام'
    _order = 'punch_time desc'

    # الحقول التي سيتم تخزين البيانات بها
    emp_code = fields.Char(string="كود الموظف في البصمة", required=True, index=True)
    punch_time = fields.Datetime(string="وقت البصمة (توقيت أودو)", required=True)
    biotime_original_time = fields.Char(string="الوقت الأصلي في بيو تايم")
    punch_state = fields.Selection([
        ('0', 'دخول'),
        ('1', 'خروج')
    ], string="الحالة")
    synced_date = fields.Datetime(string="تاريخ السحب", default=fields.Datetime.now)


class BioTimeSyncProvider(models.Model):
    _name = 'biotime.sync.provider'
    _description = 'مزامن نظام بصمة بيو تايم مستقل'

    name = fields.Char(string="اسم السيرفر", default="سيرفر BioTime الرئيسي", required=True)
    biotime_url = fields.Char(string="رابط الـ API", default="http://192.168.1.100:8081", required=True)
    api_token = fields.Char(string="مفتاح الدخول (Token)", required=True)

    def fetch_biotime_attendance(self):
        """دالة سحب الحركات وحفظها في الجدول المستقل"""
        endpoint = f"{self.biotime_url.strip('/')}/api/attendance/"
        headers = {
            'Authorization': f'Token {self.api_token}',
            'Content-Type': 'application/json'
        }

        # ضبط المنطقة الزمنية لتحويل التوقيت بدقة
        local_tz = pytz.timezone('Africa/Cairo')  # لمصر استخدم 'Africa/Cairo'   Asia/Riyadh
        utc_tz = pytz.utc

        try:
            response = requests.get(endpoint, headers=headers, timeout=20)
            if response.status_code != 200:
                return False

            data = response.json()
            transactions = data.get('results', [])

            for row in transactions:
                emp_code = row.get('emp_code')
                punch_time_str = row.get('punch_time')
                punch_state = row.get('punch_state')

                if not emp_code or not punch_time_str:
                    continue

                # تحويل التوقيت المحلي القادم من بيو تايم إلى UTC الخاص بأودو
                naive_punch_time = datetime.strptime(punch_time_str, '%Y-%m-%d %H:%M:%S')
                local_punch_time = local_tz.localize(naive_punch_time)
                utc_punch_time = local_punch_time.astimezone(utc_tz)
                odoo_datetime_str = utc_punch_time.strftime('%Y-%m-%d %H:%M:%S')

                # التحقق من عدم تكرار نفس الحركة (بناءً على الموظف والوقت) لعدم ملء قاعدة البيانات بحركات مكررة
                already_exists = self.env['biotime.raw.log'].search([
                    ('emp_code', '=', emp_code),
                    ('biotime_original_time', '=', punch_time_str)
                ], limit=1)

                if not already_exists:
                    # إنشاء السجل في الجدول المستقل الجديد
                    self.env['biotime.raw.log'].create({
                        'emp_code': emp_code,
                        'punch_time': odoo_datetime_str,
                        'biotime_original_time': punch_time_str,
                        'punch_state': punch_state,
                    })

        except Exception as e:
            return False
        return True
