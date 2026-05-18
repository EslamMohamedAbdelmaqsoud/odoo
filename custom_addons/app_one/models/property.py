from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
import requests


class Property(models.Model):
    _name = 'property'
    _description = 'Property'  # to define the name of the model in the database
    _inherit = ['mail.thread', 'mail.activity.mixin']  # to add chatter and activities

    ref = fields.Char(default='New', readonly=1)  # to generate a reference number for each property ( Add Sequences )
    name = fields.Char(required=1, default='New Property')
    phone = fields.Char(required=1, size=11)
    email = fields.Char(required=1, )
    description = fields.Text(tracking=1)
    postcode = fields.Char(required=1, size=5)
    data_availability = fields.Date(tracking=True)
    expected_selling_data = fields.Date(
        tracking=True)  # automated action to check if the expected selling data is passed or not
    is_late = fields.Boolean()
    expected_price = fields.Float()
    selling_price = fields.Float()
    diff = fields.Float(compute='_compute_diff', store=True, )
    bedrooms = fields.Integer(required=1)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ], default='north')
    owner_id = fields.Many2one('owner')
    tag_ids = fields.Many2many('tag')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed'),
    ], default='draft')
    owner_phone = fields.Char(related='owner_id.phone')
    owner_email = fields.Char(related='owner_id.email')
    line_ids = fields.One2many('property.line', 'property_id')
    active = fields.Boolean(string='Active',
                            default=True)  # to make the record active or inactive ( Features Archiving )
    create_time = fields.Datetime(string='Create Time',
                                  default=fields.Datetime.now())  # to get the create time of the record
    # to compute the next time to contact the owner ( 6 hours after the create time ) and to show it in the form view
    next_time = fields.Datetime(string='Next Time', compute='_compute_next_time_')

    @api.depends('create_time')
    def _compute_next_time_(self):
        for rec in self:
            if rec.create_time:
                rec.next_time = rec.create_time + timedelta(hours=6)
            else:
                rec.next_time = False

    # Validation ( data base ) SQL Constraints
    _sql_constraints = [('unique_name', 'unique(name)', 'The name is Exist!'),
                        ('unique_phone', 'unique(phone)', 'The phone is Exist!'),
                        ('unique_email', 'unique(email)', 'The email is Exist!')
                        ]

    # Validation to check bedrooms ( logic = python codes) API Constraints
    @api.constrains('bedrooms')
    def _check_bedrooms_greater_zero(self):  #
        for rec in self:
            if rec.bedrooms == 0:
                raise ValidationError('Please add valid number of bedrooms')

    ########################## Compute Method ##########################
    @api.depends('expected_price', 'selling_price')
    def _compute_diff(self):
        for rec in self:
            print("inside compute method")
            rec.diff = rec.expected_price - rec.selling_price

    ############################ Onchange ##############################
    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        for rec in self:
            print("inside onchange method")
            if rec.expected_price < 10000:
                return {
                    'warning': {
                        'title': 'Low Expected Price',
                        'message': 'The expected price is too low. Please consider increasing it.',
                        'type': 'notification',
                    }
                }
        return None

    ######################### Action Buttons ############################
    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state, 'draft')
            rec.state = 'draft'

    #####################################################
    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending')
            rec.write({'state': 'pending'})

    #####################################################
    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold')
            rec.state = 'sold'

    ####################### Server action ##############################
    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state = 'closed'

    ######################### Automated action ###################################################

    def check_expected_selling_data(self):
        property_ids = self.search([('state', '=', 'closed')])
        for rec in property_ids:
            if rec.expected_selling_data and rec.expected_selling_data < fields.Date.today():
                rec.is_late = True
            else:
                rec.is_late = False

    def action(self):
        print(
            self.env['property'].search(['|', ('name', '=', 'property 1'), ('postcode', '!=',
                                                                            '12345')]))  # to search for a record in the property model using the name or the postcode

        # print(self.env['owner'].create(
        #     {'name': 'owner 2',
        #      'phone': '010378852',
        #      'email': 'sdsdadd',
        #      }
        # ))  # to get all records of owner model

        # CRUD Methods:
        # 1- Create
        ########################### Create method to generate reference number for each property using sequences ( to override the create method )

    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('property_sequence')
        return res

    ################################################################

    def create_history_record(self, old_state, new_state, reason=""):
        for rec in self:
            rec.env['property.history'].create({
                'user_id': rec.env.uid,
                'property_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or ""
            })

    # to open the wizard from the button
    def action_open_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context'] = {'default_property_id': self.id}
        return action

    # to open the related owner form view from the  smart button
    def action_open_related_owner(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.owner_action')
        view_id = self.env.ref('app_one.owner_form_view').id
        action['res_id'] = self.owner_id.id
        action['views'] = [[view_id, 'form']]
        return action

    # ########################################

    #     # 2- Read = _Search
    #     @api.model
    #     def _search(self, domain, offset=0, limit=None, order=None, access_rights=None):
    #         res = super(Property, self)._search(domain, offset, limit, order, access_rights)
    #         print("inside search method")
    #         return res
    # ######################################
    #     # 3- Update = Write
    #     def write(self, vals):
    #         res = super(Property, self).write(vals)
    #         print("inside write method")
    #         return res
    # ######################################
    #     # 4- Delete = Unlink
    #     def unlink(self):
    #         res = super(Property, self).unlink()
    #         print("inside unlink method")
    #         return res

    ######################################### API Method ##################################################
    # to get the properties from the database and return them in a list of dictionaries ( to be used in the API )
    def get_properties(self):
        payload = dict()  # to store the properties in a list of dictionaries
        try:
            response = requests.get('http://localhost:8069/v1/properties',
                                    data=payload)  # to send a get request to the API endpoint to get the properties
            if response.status_code == 200:
                print("Success!")
                print(
                    response.json())  # to print the response from the API ( the list of properties in a list of dictionaries )
            else:
                print("Error!")
        except Exception as error:
            raise ValidationError(str(error))

    ############################################### Methods XLSX Report #####################################################
    def property_xlsx_report(self):
        active_ids = self.env.context.get('active_ids')
        return {
            'type': 'ir.actions.act_url',
            'url': f'/property/excel/report/{active_ids}',
            'target': 'new'
        }


# Adding Lines in Page
class PropertyLine(models.Model):
    _name = 'property.line'

    area = fields.Float()
    description = fields.Char()
    property_id = fields.Many2one('property')
