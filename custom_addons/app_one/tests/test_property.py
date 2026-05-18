from odoo.tests.common import TransactionCase
from odoo import fields


class TestProperty(TransactionCase):

    # Override the setUp method to initialize the test environment for the Property model
    def setUp(self, *args, **kwargs):
        super(TestProperty, self).setUp()  # Call the parent setUp method to initialize the test environment.

        self.property_01_record = self.env['property'].create(
            {
                'name': 'property 1000',
                'phone': '010378852',
                'email': 'es11@gmail.com',
                'postcode': '12345',
                'description': 'this is a description for property 1000',
                'data_availability': fields.Date.today(),
                'bedrooms': 5,
            })  # Create a new record in the Property model with the specified field values

    def test_01_property_values(self):
        # Test method to verify the field values of the created Property record
        property_id = self.property_01_record
        self.assertRecordValues(property_id, [{
            'name': 'property 1000',
            'phone': '010378852',
            'email': 'es11@gmail.com',
            'postcode': '12345',
            'description': 'this is a description for property 1000',
            'data_availability': fields.Date.today(),
            'bedrooms': 5,
        }])  # Assert that the field values of the created Property record match the expected values
