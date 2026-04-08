from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Student(models.Model):
    _name = 'student'
    _description = 'Student'  # to define the name of the model in the database
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    ref = fields.Char(default='New', readonly=1)  # to generate a reference number for each property ( Add Sequences )
    name = fields.Char(string='Name', required=True, default='New Student', tracking=True)
    birth_date = fields.Date(string='Birth Date')
    age = fields.Integer(compute='_compute_age', store=True, string='Age')
    grade = fields.Float(string='Grade', digits=(0, 5))
    ssn_id = fields.Char(string='SSN ID', tracking=True)
    address = fields.Text(string='Address', tracking=True)
    phone_number = fields.Char(string='Phone Number', required=1, size=11, tracking=True)
    email = fields.Char(string='Email', required=1)
    enrollment_date = fields.Date(string='Enrollment Date')
    active = fields.Boolean(string='Active',
                            default=True)  # to make the record active or inactive ( Features Archiving )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ])
    level = fields.Selection([
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('second', 'Second'),
        ('tertiary', 'Tertiary'),
        ('senior', 'Senior'),
        ('other', 'Other')
    ])
    language = fields.Selection([
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('fr', 'French'),
    ], default='ar')
    image = fields.Binary(string='Image', attachment=True)
    course_id = fields.Many2one('course')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed'),
    ], default='draft')
    course_final_price = fields.Float(related='course_id.final_price')
    class_id = fields.Many2one('classs', string='Class')
    year_id = fields.Many2one(related='class_id.year_id')
    subject_ids = fields.One2many('subject', 'student_id', string='Subjects')
    teacher_id = fields.Many2one('res.users', string='Teacher')

    # Sql Constraint Validation ( data base )
    _sql_constraints = [('unique_name', 'unique(name)', 'The name is Exist!'),
                        ('unique_phone', 'unique(phone_number)', 'The phone is Exist!'),
                        ('unique_email', 'unique(email)', 'The email is Exist!')
                        ]

    # Api Constraint Validation to check grade ( logic = python codes)
    @api.constrains('grade')
    def _check_grade_less_65(self):  #
        for rec in self:
            if rec.grade < 65:
                raise ValidationError('Please add valid grade greater than 65!')

    # Api Constraint Validation to check birth_date ( logic = python codes)
    @api.constrains('birth_date')
    def _check_birth_date(self):  #
        for rec in self:
            # Check minimum age is 7 years old
            if rec.birth_date:
                today = fields.Date.today()
                age = today.year - rec.birth_date.year
                if (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day):
                    age -= 1
                if age < 7:
                    raise ValidationError('Student must be at least 7 years old to enroll in the school!')

    ####################### Computed Method Field: ( age ) ########################
    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = fields.Date.today()
                age = today.year - rec.birth_date.year
                if (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day):
                    age -= 1
                rec.age = age
            else:
                rec.age = 0

    ######################### Action Buttons ############################
    def action_draft(self):
        for rec in self:
            print("inside action_draft method")
            rec.state = 'draft'

    #####################################################

    def action_pending(self):
        for rec in self:
            print("inside action_pending method")
            rec.write({'state': 'pending'})

    #####################################################

    def action_sold(self):
        for rec in self:
            print("inside action_sold method")
            rec.state = 'sold'

    ####################### Server action ##############################

    def action_closed(self):
        for rec in self:
            rec.state = 'closed'

    ############################################################################

    # CRUD Methods:
    # 1- Create
    ########################### Create method to generate reference number for each student using sequences ( to override the create method )
    @api.model
    # @api.model_create_multi
    def create(self, vals):
        res = super(Student, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('student_sequence')
        return res

    # ########################################
    # # 2- Read = _Search
    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights=None):
    # #     res = super(Student, self)._search(domain, offset, limit, order, access_rights)
    # #     print("inside search method")
    # #     return res
    # #
    # # ######################################
    # # 3- Update = Write
    # # def write(self, vals):
    # #     res = super(Student, self).write(vals)
    # #     print("inside write method")
    # #     return res
    # #
    # # ######################################
    # # 4- Delete = Unlink
    # # def unlink(self):
    # #     res = super(Student, self).unlink()
    # #     print("inside unlink method")
    # #     return res
