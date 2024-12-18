from odoo import http
from odoo.http import request, Response
import json
import logging


class WakaGroupController(http.Controller):
    @http.route('/v1/accounting_groups', type='http', auth='public', methods=['GET'], csrf=False)
    def get_waka_groups(self):
        try:
            # Search for groups with the is_waka_group set to True
            waka_groups = request.env['res.groups'].sudo().search([('is_waka_group', '=', True)])

            # Extract the names of the groups
            group_names = waka_groups.mapped('name')

            # Return the list of names as a JSON response
            response_data = {'accounting_groups': group_names}
            return Response(json.dumps(response_data), content_type='application/json', status=200)

        except Exception as e:
            # Handle any exceptions and return an error message
            error_response = {
                'error': 'An error occurred while retrieving waka group names',
                'details': str(e)
            }
            return Response(json.dumps(error_response), content_type='application/json', status=500)

    @http.route('/v1/roles', type='http', auth='public', methods=['POST'], website=False, cors='*', csrf=False)
    def create_waka_group(self, **post):
        try:
            # Extract the Bearer token from the request headers
            bearer_token = request.httprequest.headers.get('Authorization', '').split(' ')[-1]
            if not bearer_token:
                logging.info("*********** Roles data missing ***************")
                return Response(
                    json.dumps({'error': {'code': '401', 'message': 'Authorization token is missing or invalid.'}}),
                    status=401,
                    content_type='application/json'
                )

            # Perform token validation here
            bearer = request.env['api.keys.config'].sudo().search([('name', '=', 'Bearer'), ('secret_key', '=', bearer_token)], limit=1)

            if not bearer:
                return Response(
                    json.dumps({'error': {'code': '401', 'message': 'Invalid or missing Bearer token.'}}),
                    status=401,
                    content_type='application/json'
                )

            data = request.httprequest.data
            data = data.decode('utf-8')
            data = json.loads(data)
            logging.info("*********** Roles data  ***************%s",data)
            if not data:
                logging.info("*********** Data not found ***************")
                return Response(
                    json.dumps({'error': {'code': 404, 'message': 'Data not found'}}),
                    status=404,
                    content_type='application/json'
                )

            # Extract parameters from the request
            role_name = data.get('role_name')

            company_id = request.env['res.company'].sudo().search([('id', '=', data.get('accounting_company_id'))], limit=1)
            if not company_id:
                logging.info("*********** Company not found ***************")
                return Response(
                    json.dumps({'error': {'code': 404, 'message': 'Company not found'}}),
                    status=404,
                    content_type='application/json'
                )

            accounting_group = request.env['res.groups'].sudo().search([('name', '=', data.get('accounting_group'))], limit=1)
            if not accounting_group:
                logging.info("*********** Accounting group not found ***************")
                return Response(
                    json.dumps({'error': {'code': 404, 'message': 'Accounting Role not found'}}),
                    status=404,
                    content_type='application/json'
                )

            # Validate required fields
            if not role_name or not company_id or not accounting_group:
                return Response(
                    json.dumps({'error': {'code': 400, 'message': 'Required data missing'}}),
                    status=400,
                    content_type='application/json'
                )

            if data.get('accounting_role_id'):
                accounting_role =  request.env['waka.roles'].sudo().search([
                ('id', '=', data.get('accounting_role_id')),], limit=1)


                logging.info("*********** Updating  Role ***************%s",accounting_role)
                # Update the existing role
                update_role = accounting_role.sudo().write({
                    'role_name': role_name,
                    'company_id': company_id.id,
                    'accounting_group': accounting_group.id,
                })

                return Response(
                json.dumps({
                    'message': 'Role Updated successfully',
                    'accounting_role_id': accounting_role.id,
                }),
                status=201,
                content_type='application/json'
            )

            # Check if the role already exists for the company
            existing_role = request.env['waka.roles'].sudo().search([
                ('role_name', '=', role_name),
                ('company_id', '=', company_id.id)
            ], limit=1)

            if existing_role:
                return Response(
                    json.dumps({'error': {'code': 400, 'message': 'Role with this name already exists for this company'}}),
                    status=400,
                    content_type='application/json'
                )

            # Create the new role
            new_role = request.env['waka.roles'].sudo().create({
                'role_name': role_name,
                'company_id': company_id.id,
                'accounting_group': accounting_group.id,
            })

            # Return the newly created role details
            return Response(
                json.dumps({
                    'message': 'Role created successfully',
                    'accounting_role_id': new_role.id,
                }),
                status=201,
                content_type='application/json'
            )

        except Exception as e:
            return Response(
                json.dumps({'error': {'code': 500, 'message': str(e)}}),
                status=500,
                content_type='application/json'
            )
