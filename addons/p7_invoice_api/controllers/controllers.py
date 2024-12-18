# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import logging
import json
from datetime import datetime
import pprint
import requests
import base64
import logging
class P7InvoiceApi(http.Controller):

    @http.route('/wakatech/menus', auth='public',type='http', methods=['POST'], website=False, cors='*', csrf=False)
    def wakatech_menus(self, **kw):
        
        """Process the incoming JSON request to create/update menu items with logos in res.users."""
        data = request.httprequest.data
        data = json.loads(data)        
    
        logging.info("===========menu data========= %s", data)
        user = request.env['res.users'].sudo().search([('login','=',data.get('userId'))])
        if user:
            user.menus = False
            menu_line_item_vals = {}
            for menu in data.get('sidenav_data'):
                submenu_ids_lst = []
                menu_line_item_vals.update({'main_menu':menu.get('main_menu'),'main_menu_id':menu.get('main_menu_id'),'menu_id':user.id,'logo':menu.get('logo')})
                                    
                for submenu in menu.get('sub_menus'):
                    menu_exist = request.env['menu.list'].sudo().search([('name_id','=',submenu.get('name_id'))])
                    if menu_exist:
                        submenu_ids_lst.append(menu_exist.id)
                    else:
                        menu_vals = {'name':submenu.get('name'),'name_id':submenu.get('name_id'),'url':submenu.get('url'),'logo':submenu.get('logo')}
                        
                        create_menu = request.env['menu.list'].sudo().create(menu_vals)
                        submenu_ids_lst.append(create_menu.id)
                menu_line_item_vals.update({'submenu_ids':[(6,0,submenu_ids_lst)]})
                user.sudo().write({'menus':[(0,0,menu_line_item_vals)]})
            logging.info("===========menu created=========")
            return "Menus created"
        else:
            return "User does not exist"    

    # redirect to Accounting dashboard when Dasboard menu is clicked in the waka platform
    @http.route('/Waka-Accounting', auth='public',type='json', methods=['POST'], website=False, cors='*', csrf=False)
    def redirect_waka_accounting(self, **kw):
        data = request.httprequest.data
        data = data.decode('utf-8')
        data = json.loads(data)
        logging.info(" ******/Waka-Accounting data******** %s \n", data)
        bearer_token = request.httprequest.headers.get('Authorization', '')
        logging.info(" ******/Waka-Accounting headers ******** %s \n", bearer_token)
        if not bearer_token:
            return {'error': {'code': '401', 'message': 'Authorization token is missing.'}}

        if not data:
            return {'error': 'Data not found','code':404}

        return {'success':True ,'code':200, 'message':'development under progress...'}

    # @http.route('/v1/create/invoice', auth='public',type='json', methods=['POST'], website=False, cors='*', csrf=False)
    # def create_invoice(self, **kw):
    #     try:
    #         # Extract the Bearer token from the request headers
    #         bearer_token = request.httprequest.headers.get('Authorization', '').split(' ')[-1]
    #         if not bearer_token:
    #             return {'error': {'code': '401', 'message': 'Authorization token is missing or invalid.'}}
    #         # Perform token validation here
    #         bearer = request.env['api.keys.config'].sudo().search([('name','=','Bearer'),('secret_key', '=', bearer_token)], limit=1)
    #         if not bearer:
    #             return {'error': {'code': '401', 'message': 'Invalid or missing Bearer token.'}}
    #         data = request.httprequest.data
    #         data = data.decode('utf-8')
    #         data = json.loads(data)
    #         logging.info("*********** invoice data ***************%s",data)
    #         if not data:
    #             return {'error': 'Data not found','code':404,'success':False}     
    #         # required_fields = [
    #         #     "consumer_company_id",
    #         #     "provider_company_id",
    #         #     "payment_term_id",
    #         #     "currency_id",
    #         #     "journal_id",
    #         #     "invoice_date",
    #         #     "invoice_lines"
    #         # ]
    #         # missing_fields = [field for field in required_fields if field not in data]
    #         # if missing_fields:
    #         #     raise {'error':f"Missing required fields: {', '.join(missing_fields)}",'success':False}       
    #         invoice_lines = data.get('invoice_lines', [])

    #         provider = int(data.get('provider_company_id'))
    #         print("==========",type(provider),provider)
    #         from_company = request.env['res.company'].sudo().browse(int(data.get('provider_company_id')))   # from company_id
    #         print("--------from_company---------",from_company.name)
    #         if not from_company:
    #             return {'error': f'Provider Company {provider} not exist','code':404,'success':False}       
    #         consumer = int(data.get('consumer_company_id'))
    #         to_company = request.env['res.company'].sudo().browse(consumer)   # to company_id
    #         print("--------to_company---------",to_company.name)
    #         if not to_company:
    #             return {'error': f'Consumer Company {consumer} not exist','code':404,'success':False}       
    #         invoice_date_str = data.get('invoice_date')
    #         if invoice_date_str:
    #             invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    #         else:
    #             return {'error': 'Missing param invoice_date.','code':404}
    #         # if not data.get('to_company_id') or not invoice_lines:
    #         #     return {'error': 'Missing To company_id or invoice_lines. not found'}       
    #         # Prepare invoice lines
    #         invoice_line_values = []
    #         for line in invoice_lines:
    #             tax_ids = line.get('tax_ids', [])
    #             if isinstance(tax_ids, list):
    #                 tax_ids = [(6, 0, tax_ids)]  # Correctly format for many-to-many relationship
    #             else:
    #                 tax_ids = [(6, 0, [tax_ids])]  # In case tax_ids is passed as a single value
    #             invoice_line_values.append((0, 0, {
    #                     'product_id': line.get('product_id'),
    #                     'account_id': line.get('account_id'),
    #                     'quantity': line.get('quantity'),
    #                     'price_unit': line.get('price_unit'),
    #                     'tax_ids': tax_ids
    #                 }
    #             ))
    #         print("========invoice_line_values=========",invoice_line_values)
    #         errr
    #         # Create an invoice
    #         invoice = request.env['account.move'].sudo().create({
    #             'move_type': 'out_invoice',
    #             'partner_id': to_company.partner_id.id,
    #             'journal_id': data.get('journal_id'),
    #             'invoice_payment_term_id' : data.get('payment_term_id'),
    #             'company_id' : from_company.id,    # from company_id
    #             'currency_id': data.get('currency_id'),
    #             'invoice_date': invoice_date,
    #             'invoice_line_ids': invoice_line_values
    #         })       
    #         invoice.action_post()             # Confirm the invoice to validate and post it
    #         logging.info(" ************** Invoice Created ************** %s",invoice)
    #         return json.dumps({'response': {'code': '201', 'message': 'Invoice created successfully.','invoice_id':invoice.id,'success':True}})   
    #     except Exception as e:
    #         logging.exception("Error occurred while creating Invoice: %s", str(e))
    #         return {'error': str(e),'success':False}

    @http.route('/v1/create/invoice', type='json', auth='public', methods=['POST'], website=False, cors='*', csrf=False)
    def create_invoice(self, **params):
        try:
            data = request.httprequest.data
            data = data.decode('utf-8')
            data = json.loads(data)
            logging.info("*********** invoice data ***************%s",data)
            if not data:
                return {'error': 'Data not found','code':404,'success':False}
            required_fields = [
                "consumer_company_id",
                "provider_company_id",
                "payment_term_id",
                "currency_id",
                "journal_id",
                "invoice_date",
                "invoice_lines"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return {'error':f"Missing required fields: {', '.join(missing_fields)}",'success':False}

            invoice_lines = data.get('invoice_lines')
            to_company = request.env['res.company'].sudo().browse(data.get('consumer_company_id'))
            partner_id = to_company.partner_id.id
            
            # Prepare invoice lines
            invoice_line_values = []
            for line in invoice_lines:
                tax_ids = line.get('tax_ids', [])
                if isinstance(tax_ids, list):
                    tax_ids = [(6, 0, tax_ids)]  # Correctly format for many-to-many relationship
                else:
                    tax_ids = [(6, 0, [tax_ids])]  # In case tax_ids is passed as a single value
                invoice_line_values.append((
                    0, 0, {
                        'product_id': line.get('product_id'),
                        'account_id': line.get('account_id'),
                        'quantity': line.get('quantity'),
                        'price_unit': line.get('price_unit'),
                        'tax_ids': tax_ids
                    }
                ))
            print("========invoice_line_values=========",invoice_line_values)   
            
            # Create an invoice
            invoice = request.env['account.move'].sudo().create({'move_type': 'out_invoice',
                                                                'partner_id': partner_id,    # Customer/Consumer
                                                                'journal_id': data.get('journal_id'),
                                                                'invoice_payment_term_id' : data.get('payment_term_id'),
                                                                'company_id' : data.get('provider_company_id'),   # From company_id
                                                                'currency_id': data.get('currency_id'),
                                                                'invoice_date': data.get('invoice_date'),
                                                                'invoice_line_ids': invoice_line_values
                                                                })
            logging.info(" ************** Invoice Created ************** %s",invoice)
            # Confirm the invoice to validate and post it
            invoice.action_post()
            
            return {'response': {'code': '201', 'message': 'Invoice created successfully.','invoice_id':invoice.id,'success':True}}
        except Exception as e:
            logging.exception("Error occurred while creating invoice: %s", str(e))
            return {'error': str(e),'success':False}
        
    # @http.route('/api/logout', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    # def logout_user(self, uid=None, sid=None):
    #     """API endpoint to log out a session using session ID and user ID"""
    #     # Ensure data is fetched from the request body (JSON)
    #     data = request.httprequest.get_json()
    #     print("===============data==============", data)

    #     # If uid or sid is not provided in the request, use hardcoded values for testing
    #     uid = data.get('uid')
    #     sid = data.get('sid')
    #     print("===============sid,uid==============", sid,uid)

    #     if not uid or not sid:
    #         return {'status': 400, 'message': 'User ID or Session ID are required'}

    #     # Find the session in the current request
    #     user_sessions = self._find_session(uid, sid)
    #     print("===========user_sessions==========",user_sessions)

    #     if not user_sessions:
    #         return {'status': 404, 'message': 'Session not found'}
    #     print("===========user_sessions==========",user_sessions.uid)
    #     print("===========user_sessions==========",user_sessions.sid)
    #     # Terminate the session
    #     terminated = self._terminate_session(user_sessions)
    #     print("===========terminated==========",terminated)
    #     if terminated:
    #         return {'status': 200, 'message': 'Session successfully terminated'}
    #     else:
    #         return {'status': 500, 'message': 'Session termination failed'}

    # def _find_session(self, uid, sid):
    #     """Find a session using uid and sid"""
    #     session_store = http.root.session_store  # Get session store from Odoo's HTTP framework
    #     session = session_store.get(sid)

    #     if session and session.uid == uid:
    #         return session
    #     return None

    # def _terminate_session(self, session):
    #     """Terminate the user session by explicitly removing it from the session store"""
    #     try:
    #         # Remove the session from the session store
    #         http.root.session_store.delete(session)
    #         logging.info("======= _terminate_session ===========")
    #         return True
    #     except Exception as e:
    #         return False
    #     # """Terminate the user session"""
    #     # try:
    #     #     session.logout(keep_db=True)  # Use the logout method provided by Odoo's session framework
    #     #     return True
    #     # except Exception as e:
    #     #     return False
