# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import logging
import json
from datetime import datetime
import logging
from cryptography.fernet import Fernet

class P7UserApi(http.Controller):

    @http.route('/v1/create/user', auth='public',type='json', methods=['POST'], website=False, cors='*', csrf=False)
    def create_user(self, **kw):
        try:
            # Extract the Bearer token from the request headers
            bearer_token = request.httprequest.headers.get('Authorization', '').split(' ')[-1]
            if not bearer_token:
                return {'error': {'code': '401', 'message': 'Authorization token is missing or invalid.'}}

            # Perform token validation here
            bearer = request.env['api.keys.config'].sudo().search([('name','=','Bearer'),('secret_key', '=', bearer_token)], limit=1)
            if not bearer:
                return {'error': {'code': '401', 'message': 'Invalid or missing Bearer token.'}}
            data = request.httprequest.data
            data = data.decode('utf-8')
            data = json.loads(data)
            logging.info("*********** create User data ***************%s",data)

            if not data:
                logging.info("*********** data not found ***************")
                return {'error': 'Data not found','code':404}

            waka_company = request.env['res.company'].sudo().search([('waka_company_id','=',data.get('company_id'))],limit=1)
            if not waka_company:
                logging.info("*********** Company not found ***************")
                return {'error': {'code': '404', 'message': 'Company not found'}}

            user_login = request.env['res.users'].sudo().search([('login', '=', data.get("email"))], limit=1)
            if user_login:
                if waka_company.id not in user_login.company_ids.ids:    # checking allowed companies
                    existing_user.company_ids = [(4,waka_company)]
                return {'error': {'code': '401', 'message': 'Login email already exist'}}


            existing_user = request.env['res.users'].sudo().search([('wakatech_id', '=', data.get("wakatech_user_id"))], limit=1)
            if existing_user:
                logging.info("*********** User already exist ***************%s",existing_user)
                return {'error': {'code': '401', 'message': 'User already exist'}}

            else:
                login_pass = request.env['api.keys.config'].sudo().search([('name','=','login_pass')], limit=1).secret_key
                access = 'Read-only'   # setting default Accounting access Read-only for all the newly created users
                if data.get("user_accounting_access"):
                    logging.info("*********** data.get(user_accounting_access) ***************%s",data.get("user_accounting_access"))
                    access = request.env['res.groups'].sudo().search([('name', '=',data.get("user_accounting_access"))],limit=1).id   # if roles are provided in the request, accounting access will be updated

                accounting_dashboard_id = request.env['ir.actions.actions'].sudo().search([('name','=','Accounting Dashboard')], limit=1) #map the Accounting Dashboard as Home action
                user_vals={
                    "name": data.get("contact_name"),
                    "login": data.get("email"),
                    "email": data.get("email"),
                    "mobile": data.get("mobile"),
                    "password":  login_pass,
                    "company_id": waka_company.id,
                    "company_ids":[waka_company.id],
                    "lang": "en_US",
                    "groups_id": [(4, access)],
                    "wakatech_id":  data.get("wakatech_user_id"),
                    "wechat_id": data.get("wechat_id"),
                    "action_id":accounting_dashboard_id.id
                }

                create_user = request.env['res.users'].sudo().create(user_vals)
                logging.info(" ************** user Created SUCCESS ************** %s",create_user.id)
                return {'response': {'code': '201', 'message': 'Accounting user created.','waka_user_id' : data.get("wakatech_user_id"),'accounting_user_id' : create_user.id}}

        except Exception as e:
            logging.exception("Error occurred while creating the User: %s", str(e))
            return {'error': str(e),'success':False}

    @http.route('/v1/invite/user', auth='public',type='json', methods=['POST'], website=False, cors='*', csrf=False)
    def invite_user(self, **kw):
        try:
            # Extract the Bearer token from the request headers
            bearer_token = request.httprequest.headers.get('Authorization', '').split(' ')[-1]
            if not bearer_token:
                return {'error': {'code': '401', 'message': 'Authorization token is missing or invalid.'}}

            # Perform token validation here
            bearer = request.env['api.keys.config'].sudo().search([('name','=','Bearer'),('secret_key', '=', bearer_token)], limit=1)
            if not bearer:
                return {'error': {'code': '401', 'message': 'Invalid or missing Bearer token.'}}
            data = request.httprequest.data
            data = data.decode('utf-8')
            data = json.loads(data)
            logging.info("*********** invite_user data ***************%s",data)
            if not data:
                logging.info("*********** data not found ***************")
                return {'error': 'Data not found','code':404}

            invited_company = request.env['res.company'].sudo().browse(data.get('invited').get('accounting_company_id'))
            invited_user = request.env['res.users'].sudo().browse(data.get('invited').get('accounting_company_id'))

            if data.get('invitee').get('accounting_user_id'):
                invitee_user = request.env['res.users'].sudo().search([('id','=',data.get('invitee').get('accounting_user_id'))],limit=1)
                logging.info("*********** invitee_user ***************%s",invitee_user)

                if not invitee_user:
                    return {'error': {'code': '404', 'message': 'The provided Invitee Accounting User not found'}}
                invitee_user.company_ids = [(4,invited_company.id)]
                invited_company.internal_team_members_ids = [(4,invitee_user.id,0)] #linking the invitee User as an Internal team
            else:
                user = data.get('user')
                login_pass = request.env['api.keys.config'].sudo().search([('name','=','login_pass')], limit=1).secret_key
                # access = 'Accountant'
                access = request.env['res.groups'].sudo().search([('name', '=','Accountant')],limit=1).id  # this logic will be changed in future
                accounting_dashboard_id = request.env['ir.actions.actions'].sudo().search([('name','=','Accounting Dashboard')], limit=1) #map the Accounting Dashboard as Home action
                user_vals={
                    "name": user.get("contact_name"),
                    "login": user.get("email"),
                    "email": user.get("email"),
                    "mobile": user.get("mobile"),
                    "password":  login_pass,
                    "company_id": invited_company.id,
                    "company_ids":[(4,invited_company.id)],
                    "lang": "en_US",
                    "groups_id": [(4, access)],
                    "wakatech_id":  user.get("waka_user_id"),
                    "wechat_id": user.get("wechat_id"),
                    "action_id":accounting_dashboard_id.id
                }

                invitee_user = request.env['res.users'].sudo().create(user_vals)
                logging.info(" ************** user Created SUCCESS ************** %s",invitee_user.id)
                invited_company.internal_team_members_ids = [(4,invitee_user.id,0)] #linking the created User as an Internal team
                role = request.env['waka.roles'].sudo().search([('id', '=',int(user.get("role_id")))],limit=1)
                logging.info(" ************** Provided Role ************** %s",role)
                role.write({'user_ids': [(4,invitee_user.id,0)]}) if role else False   #linking the created user to the provided role
 
            return {'success':True,'message': 'User Invite Mapped successfully',
                'invitee_waka_user_id':invitee_user.wakatech_id,
                'invitee_accounting_user_id': invitee_user.id,
                'invitee_waka_company_id':invited_company.waka_company_id,
                'invitee_accounting_company_id': invited_company.id,
                'code':200}
        except Exception as e:
            logging.exception("Error occurred while mapping the User: %s", str(e))
            return {'error': str(e),'success':False}



    # @http.route('/v1/invite/user', auth='public',type='json', methods=['POST'], website=False, cors='*', csrf=False)
    # def invite_user(self, **kw):
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
    #         logging.info("*********** invite_user data ***************%s",data)
    #         if not data:
    #             logging.info("*********** data not found ***************")
    #             return {'error': 'Data not found','code':404}

    #         waka_company = request.env['res.company'].sudo().search([('waka_company_id','=',data.get('company_id'))],limit=1)
    #         if not waka_company:
    #             logging.info("*********** Company not found ***************")
    #             return {'error': {'code': '404', 'message': 'Company not found'}}

    #         if data.get("invitee_user_id"):  # when invitee user id is given
    #             invited_user = request.env['res.users'].sudo().search([('wakatech_id', '=', data.get("contact_invited_id"))], limit=1)
    #             # if not invited_user:
    #             #     return {'error': {'code': '404', 'message': 'User not found'}}
    #             invitee_user = request.env['res.users'].sudo().search([('wakatech_id', '=', data.get("invitee_user_id"))], limit=1)
    #             print("-----------",invited_user,invitee_user)
    #             if invited_user and invitee_user:
    #                 invitee_user.contact_invite_id = invited_user.id
    #                 allowed_companies = invitee_user.company_ids.ids

    #                 if invitee_user and waka_company.id  in allowed_companies:
    #                     return {'error': {'code': '401', 'message': 'Login email already exist'}}

    #                 elif invitee_user and waka_company.id not in allowed_companies:
    #                     invitee_user.company_ids = [(4,waka_company.id)]
    #                     logging.info("*********** Internal team member mapped. SUCCESS ***************")
    #                     return  {'response': {'code': '201', 'message': 'Internal team member mapped.','accounting_user_id' : invitee_user.id}}
    #             else:
    #                 logging.info("*********** User not found ***************")
    #                 return {'error': {'code': '404', 'message': 'User not found'}}

    #             # Extract the Key  token from the request headers
    #             # login_pass = request.env['api.keys.config'].sudo().search([('name','=','login_pass')], limit=1).secret_key
    #             # if key:
    #             #     key = (key).encode('utf-8')
    #             # cipher_suite = Fernet(key)
    #             # # Encrypting the password using Key
    #             # cipher_text = cipher_suite.encrypt("admin@123".encode('utf-8'))
    #             # logging.info(" ___________________________________cypher texted %s",cipher_text)
    #             # # Decrypt cipher text
    #             # plain_text = data.get('password')
    #             # decrypted_text = cipher_suite.decrypt(plain_text.encode('utf-8')).decode('utf-8')
    #         else:  # when invitee user  is null
    #             invited_user = request.env['res.users'].sudo().search([('wakatech_id', '=', data.get("contact_invited_id"))], limit=1).id or None
    #             exisiting_invitation = request.env['invitee.users'].sudo().search([('email',"=",data.get("email")),('contact_invite_id','=',invited_user),('company_id','=',waka_company.id)])

    #             if exisiting_invitation:
    #                 logging.info("*********** Invitation already exist ***************")
    #                 return {'error': {'code': '401', 'message': 'Invitation already exist'}}

    #             invition_vals={
    #                 "name": data.get("contact_name"),
    #                 "email": data.get("email"),
    #                 "mobile": data.get("mobile"),
    #                 "company_id": waka_company.id,
    #                 "contact_invite_id": invited_user,
    #                 "wakatech_id":  data.get("wakatech_user_id"),
    #                 "wechat_id": data.get("wechat_id"),
    #             }
    #             invitee_user = request.env['invitee.users'].sudo().create(invition_vals)
    #             logging.info("*********** Invitation created SUCCESS ***************")
    #             return {'response': {'code': '201', 'message': 'Invitation created.','invitation_id':invitee_user.id}}

    #     except Exception as e:
    #         logging.exception("Error occurred while mapping the User: %s", str(e))
    #         return {'error': str(e),'success':False}
