import math
from urllib.parse import parse_qs

from PIL.ImageChops import offset

from odoo import http
from odoo.http import request
import json


# Handling Response
def valid_response(data, status, pagination_info):
    response_body = {
        "message": "Request Processed Successfully",
        "data": data,

    }
    if pagination_info:
        response_body["pagination_info"] = pagination_info
    return request.make_json_response(response_body, status=status)


def invalid_response(error, status):
    response_body = {
        "error": error,
    }
    return request.make_json_response(response_body, status=status)


# create a new controller that will contain the endpoint
class PropertyApi(http.Controller):

    # 1- ( SQl Queries : Create) a new endpoint that will create a new property record in the database
    @http.route('/v1/property', methods=["POST"], type='http', auth='none', csrf=False)
    def post_property(self):
        args = request.httprequest.data.decode()  # to get the data from the request and decode it from bytes to string
        vals = json.loads(
            args)  # to convert the string data to a dictionary that we can use to create a new record in the database
        if not vals.get('name'):
            return request.make_json_response({
                "error": "Name is required!",
            }, status=400)
        try:
            # res = request.env['property'].sudo().create(vals)
            # Sql Query to create a new record in the database using the values from the request
            cr = request.env.cr
            columns = ', '.join(vals.keys()) # --> name, phone, email, .....
            values = ', '.join(['%s'] * len(vals)) # --> '%s', '%s', '%s', ......
            query = f"""INSERT INTO property ({columns})VALUES ({values}) RETURNING id, name,phone,email,bedrooms,postcode"""
            cr.execute(query,tuple(vals.values()))
            res = cr.fetchone()
            print(res)
            if res:
                return request.make_json_response({
                    "message": "Property Created Successfully",
                    "id": res[0],
                    "name": res[1],
                    "phone": res[2],
                    "email": res[3],
                    "bedrooms": res[4],
                    "postcode": res[5],
                }, status=201)
        except Exception as error:
            return request.make_json_response({
                "error": error,
            }, status=400)

    # # 1- (Create) a new endpoint that will create a new property record in the database
    # @http.route('/v1/property', methods=["POST"], type='http', auth='none', csrf=False)
    # def post_property(self):
    #     args = request.httprequest.data.decode()
    #     vals = json.loads(args)
    #     if not vals.get('name'):
    #         return request.make_json_response({
    #             "error": "Name is required!",
    #         }, status=400)
    #     try:
    #         res = request.env['property'].sudo().create(vals)
    #         if res:
    #             return request.make_json_response({
    #                 "message": "Property Created Successfully",
    #                 "id": res.id,
    #                 "name": res.name,
    #             }, status=201)
    #     except Exception as error:
    #         return request.make_json_response({
    #             "error": error,
    #         }, status=400)

    # 1- (Create) a new endpoint that will create a new property record in the database and return the created record in json format
    @http.route('/v1/property/json', methods=["POST"], type='json', auth='none', csrf=False)
    def post_property_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        res = request.env['property'].sudo().create(vals)
        if res:
            return {
                "message": "Property Created Successfully"
            }

    # 2- (Update) the previous endpoint to return the created record in http format
    @http.route('/v1/property/<int:property_id>', methods=["PUT"], type='http', auth='none', csrf=False)
    def update_property(self, property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return request.make_json_response({
                    "error": "ID does not exist",
                }, status=400)
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            property_id.write(vals)
            return request.make_json_response({
                "message": "Property Updated Successfully",
                "id": property_id.id,
                "name": property_id.name,
            }, status=200)
        except Exception as error:
            return request.make_json_response({
                "error": error,
            }, status=400)

    # 3- (Read) endpoint to get single Record a property by id
    @http.route('/v1/property/<int:property_id>', methods=["GET"], type='http', auth='none', csrf=False)
    def get_property(self, property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return invalid_response("ID does not exist!", status=400)
            return valid_response({
                "message": "Property Read Successfully",
                "id": property_id.id,
                "name": property_id.name,
                "description": property_id.description,
                "postcode": property_id.postcode,
            }, status=200)
        except Exception as error:
            return request.make_json_response({
                "error": error,
            }, status=400)

    # 3- ReadAll( Get List  + Filtration) endpoint to get All Record a property
    @http.route('/v1/properties', methods=["GET"], type='http', auth='none', csrf=False)
    def get_all_property_list(
            self):  # to get all the properties and also to filter the properties by state using query params
        try:
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))  # to get the query params from the url
            property_domain = []  # to store the domain for the search method
            page = offset = None
            limit = 5
            if params:
                if params.get('limit'):
                    limit = int(params.get('limit')[0])
                if params.get('page'):
                    page = int(params.get('page')[0])
            if page:
                offset = (page * limit) - limit
            if params.get(
                    'state'):  # to check if the state query param is present in the url and if it is present then add it to the domain
                property_domain += [('state', '=', params.get('state')[0])]
            property_ids = request.env['property'].sudo().search(property_domain, offset=offset, limit=limit,
                                                                 order='id desc')
            property_count = request.env['property'].sudo().search_count(property_domain)
            if not property_ids:  # to check if there are no records found based on the search method and if there are no records found then return an error message in json format
                return invalid_response("There Is Are not Records!", status=400)
            return valid_response([{
                "message": "Property Read Successfully",
                "id": property_id.id,
                "name": property_id.name,
                "description": property_id.description,
                "postcode": property_id.postcode,
            } for property_id in property_ids], pagination_info={
                'page': page if page else 1,
                'limit': limit,
                'pages': math.ceil(property_count / limit) if limit else 1,
                'count': property_count,
            }, status=200)
        except Exception as error:
            return request.make_json_response({
                "error": error,
            }, status=400)

    # 4- (Delete) endpoint to delete a property by id
    @http.route('/v1/property/<int:property_id>', methods=["DELETE"], type='http', auth='none', csrf=False)
    def delete_property(self, property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return request.make_json_response({
                    "error": "ID does not exist!",
                }, status=400)
            property_id.unlink()
            return request.make_json_response({
                "message": "Property Deleted Successfully",
            }, status=200)
        except Exception as error:
            return request.make_json_response({
                "error": error,
            }, status=400)
