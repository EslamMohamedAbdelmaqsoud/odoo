from odoo import http
from odoo.http import request

class ClinicAPI(http.Controller):
    @http.route('/clinic/get_patient_info/<string:ref>', type='json', auth='user')
    def get_patient_data(self, ref):
        patient = request.env['patient'].sudo().search([('reference', '=', ref)], limit=1)
        if patient:
            return {
                'name': patient.name,
                'age': patient.age,
                'last_visit': patient.message_ids[0].date if patient.message_ids else 'No visits'
            }
        return {'error': 'Patient not found'}