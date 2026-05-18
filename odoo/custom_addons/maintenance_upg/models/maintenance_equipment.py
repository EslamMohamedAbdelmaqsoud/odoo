from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    current_reading = fields.Float(string="Current Reading", default=0.0)  # القراءة الحالية
    reading_uom = fields.Selection([
        ('km', 'Kilometers'),
        ('hrs', 'Hours'),
        ('cycles', 'Cycles'),
    ], string="Reading Unit", default='km')
    pm_plan_ids = fields.One2many('maintenance.pm.plan', 'equipment_id', string="PM Plans")


class PMPlan(models.Model):
    _name = 'maintenance.pm.plan'
    _description = 'Preventive Maintenance Plan'
    _order = 'equipment_id, interval'

    name = fields.Char(string="Plan Name", required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string="Asset", required=True, ondelete='cascade',
                                   index=True)
    interval = fields.Float(string="Interval (Reading)", required=True,
                            help='Maintenance interval in units (km, hours, etc.)')  # الفاصل الزمني[cite: 1]
    last_maintenance_reading = fields.Float(string="Last Reading at Maintenance", default=0.0,
                                            help='Last reading value when maintenance was performed')
    task_ids = fields.One2many('maintenance.pm.plan.task', 'plan_id', string="Tasks")
    item_ids = fields.One2many('maintenance.pm.plan.item', 'plan_id', string="Spare Parts")

    @api.constrains('interval')
    def _check_interval_positive(self):
        """التأكد من أن الفاصل الزمني موجب"""
        for plan in self:
            if plan.interval <= 0:
                raise ValidationError("Interval must be greater than 0")

    def _generate_maintenance_requests(self):
        """الدالة التي تفحص العداد وتنشئ الطلب تلقائياً"""
        plans = self.search([])
        for plan in plans:
            # إذا تجاوز الفرق بين القراءة الحالية وآخر صيانة "الفاصل الزمني"
            if (plan.equipment_id.current_reading - plan.last_maintenance_reading) >= plan.interval:
                request = self.env['maintenance.request'].create({
                    'name': f'Scheduled PM: {plan.name}',
                    'equipment_id': plan.equipment_id.id,
                    'maintenance_type': 'preventive',
                    'schedule_date': fields.Datetime.now(),
                })
                # نسخ المهام وقطع الغيار إلى الطلب[cite: 2]
                for task in plan.task_ids:
                    self.env['maintenance.request.task'].create({
                        'request_id': request.id,
                        'name': task.name
                    })
                for item in plan.item_ids:
                    self.env['maintenance.request.part'].create({
                        'request_id': request.id,
                        'product_id': item.product_id.id,
                        'qty': item.quantity
                    })
                plan.last_maintenance_reading = plan.equipment_id.current_reading


class PMPlanTask(models.Model):
    _name = 'maintenance.pm.plan.task'
    _description = 'PM Plan Task'
    plan_id = fields.Many2one('maintenance.pm.plan', required=True, ondelete='cascade')
    name = fields.Char(string="Task Description", required=True)


class PMPlanItem(models.Model):
    _name = 'maintenance.pm.plan.item'
    _description = 'PM Plan Spare Part'
    plan_id = fields.Many2one('maintenance.pm.plan', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Spare Part", required=True)
    quantity = fields.Float(string="Quantity", default=1.0, required=True)


# تمديد طلب الصيانة لإضافة جداول التنفيذ
class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    task_ids = fields.One2many('maintenance.request.task', 'request_id', string="Tasks")
    part_ids = fields.One2many('maintenance.request.part', 'request_id', string="Parts Used")


class MaintenanceRequestTask(models.Model):
    _name = 'maintenance.request.task'
    _description = 'Maintenance Request Task'
    request_id = fields.Many2one('maintenance.request', required=True, ondelete='cascade')
    name = fields.Char(string="Task", required=True)
    is_done = fields.Boolean(string="Done", default=False)


class MaintenanceRequestPart(models.Model):
    _name = 'maintenance.request.part'
    _description = 'Maintenance Request Spare Part'
    request_id = fields.Many2one('maintenance.request', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Part", required=True)
    qty = fields.Float(string="Quantity", required=True, default=1.0)
