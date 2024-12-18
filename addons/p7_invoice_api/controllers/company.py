# -*- coding: utf-8 -*-
from odoo import http,fields
from odoo.http import request, Response
import logging
import json




class CompanyAPIController(http.Controller):

    @http.route('/v1/create/company', type='json', auth='public', methods=['POST'], website=False, cors='*', csrf=False)
    def create_company(self, **kwargs):
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
            logging.info("*********** create_company data ***************%s",data)
            if not data:
                return {'error': 'Data not found','code':404}
            if data.get('company').get('accounting_company_id'):
                acc_company = request.env['res.company'].sudo().search([('id', '=',int(data.get('company').get('accounting_company_id')))],limit=1)
            else:      # Company Creation
                company = data.get('company')
                waka_city = request.env['waka.city.master'].sudo().search([('wakatech_city_id','=',company.get('city_id'))],limit=1)
                waka_state = request.env['res.country.state'].sudo().search([('wakatech_state_id','=',company.get('state_id'))],limit=1)
                waka_country = request.env['res.country'].sudo().search([('wakatech_country_id','=',company.get('country_id'))],limit=1)
                company_vals = {
                'waka_company_id':company.get('waka_company_id'),
                'name': company.get('company_name') +" - "+ waka_country.name,
                'company_name': company.get('company_name'),
                'company_local_name': company.get('company_local_name'),
                'company_ref_code': company.get('company_ref_code'),
                'contact_name': company.get('contact_name'),
                'email': company.get('email'),
                'phone': company.get('phone'),
                'zip': company.get('zip_code'),
                'country_id': waka_country.id if waka_country else False,
                'currency_id': waka_country.currency_id.id if waka_country else False,
                'state_id': waka_state.id if waka_state else False,
                'city_id': waka_city.id if waka_city else False,  # master ha to be synced
                'city': company.get('city_name'),
                'street': company.get('address_line_1'),
                'street2': company.get('address_line_2'),
                'website': company.get('website_address'),
                'eori_no': company.get('eori_no'),
                'export_reg_no': company.get('export_reg_no'),
                'import_reg_no': company.get('import_reg_no'),
                'inttra_id': company.get('inttra_id'),
                'scac_code': company.get('scac_code'),
                'from_invite': company.get('from_invite'),
                }
                if data.get('parent_company_id'):  #Update parent company if it exist
                    waka_parent_company = request.env['res.company'].sudo().search([('waka_company_id','=',data.get('parent_company_id'))],limit=1)
                    company_vals.update({'parent_id': waka_parent_company.id }) if waka_parent_company else False

                acc_company = request.env['res.company'].sudo().create(company_vals) # Create the company record in Accounting system
                logging.info("******company created SUCCESS *********%s",acc_company)
            
            if data.get('user').get('accounting_user_id'):
                acc_user = request.env['res.users'].sudo().search([('id', '=',int(data.get('user').get('accounting_user_id')))],limit=1)
            else:
                user = data.get('user')
                login_pass = request.env['api.keys.config'].sudo().search([('name','=','login_pass')], limit=1).secret_key
                
                access = request.env['res.groups'].sudo().search([('name', '=','Accountant')],limit=1).id   # setting default Accounting access Accountant for all newly created Admin
                if user.get("role"):
                    logging.info("*********** data.get(user_accounting_access) ***************%s",data.get("user_accounting_access"))
                    access = request.env['res.groups'].sudo().search([('name', '=',user.get("role"))],limit=1).id   # if roles are provided in the request, accounting access will be updated

                accounting_dashboard_id = request.env['ir.actions.actions'].sudo().search([('name','=','Accounting Dashboard')], limit=1)   #map the Accounting Dashboard as Home action
                user_vals={
                "name": user.get("contact_name"),
                "login": user.get("email"),
                "email": user.get("email"),
                "mobile": user.get("mobile"),
                "password":  login_pass,
                "company_id": acc_company.id,
                "company_ids":[acc_company.id],
                "lang": "en_US",
                "groups_id": [(4, access)],
                "wakatech_id":  user.get("waka_user_id"),
                "wechat_id": user.get("wechat_id"),
                "action_id":accounting_dashboard_id.id
                }
                if data.get('is_admin'):
                    user_vals.update({'is_waka_admin':True,'admin_company_ids':[(4,acc_company.id)]})   # set the user as admin

                acc_user = request.env['res.users'].sudo().create(user_vals)
                logging.info(" ************** user Created SUCCESS ************** %s",acc_user.id)
            
            logging.info(" ************** Company creation SUCCESS ************** ")
            return {                                           # Return the success message with company details
            'success':True,
            'message': 'Company and User created successfully',
            'accounting_company_id': acc_company.id,
            'waka_company_id':acc_company.waka_company_id,
            'accounting_user_id':acc_user.id,
            'waka_user_id':acc_user.wakatech_id,
            'code':200
            }

        except Exception as e:
            logging.exception("Error occurred while creating the company: %s", str(e))
            return {'error': str(e),'success':False}



    # @http.route('/v1/create/company', type='json', auth='public', methods=['POST'], website=False, cors='*', csrf=False)
    # def create_company(self, **kwargs):
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
    #         logging.info("*********** create_company data ***************%s",data)
    #         if not data:
    #             return {'error': 'Data not found','code':404}


    #           # During Company creation
    #         # waka_city = request.env['city.master'].sudo().search([('wakatech_city_id','=',data.get('city_id'))],limit=1)
    #         waka_state = request.env['res.country.state'].sudo().search([('wakatech_state_id','=',data.get('state_id'))],limit=1)
    #         waka_country = request.env['res.country'].sudo().search([('wakatech_country_id','=',data.get('country_id'))],limit=1)
    #         existing_company = request.env['res.company'].sudo().search([('waka_company_id','=',data.get('company_id'))],limit=1)
    #         if existing_company:
    #             logging.info("======= Company already exists ======")
    #             return {
    #                 'success':False,
    #                 'message': 'Company already exists',
    #                 'waka_company_id':int(existing_company.waka_company_id),
    #                 'accounting_company_id': existing_company.id,
    #                 'accounting_company_name': existing_company.name
    #             }
    #         else:
    #             company_vals = {
    #             'waka_company_id':data.get('company_id'),
    #             'name': data.get('company_name'),
    #             'company_name': data.get('company_name'),
    #             'company_local_name': data.get('company_local_name'),
    #             'company_ref_code': data.get('company_ref_code'),
    #             'contact_name': data.get('contact_name'),
    #             'email': data.get('email'),
    #             'phone': data.get('phone'),
    #             'zip': data.get('zip_code'),
    #             'country_id': waka_country.id if waka_country else False,
    #             'currency_id': waka_country.currency_id.id if waka_country else False,
    #             'state_id': waka_state.id if waka_state else False,
    #             # 'city_id': waka_city.id if waka_country else False,  # to be added in future
    #             'street': data.get('address_line_1'),
    #             'street2': data.get('address_line_2'),
    #             'website': data.get('website_address'),
    #             'eori_no': data.get('eori_no'),
    #             'export_reg_no': data.get('export_reg_no'),
    #             'import_reg_no': data.get('import_reg_no'),
    #             'inttra_id': data.get('inttra_id'),
    #             'scac_code': data.get('scac_code'),
    #             'from_invite': data.get('from_invite'),
    #             }
    #             if data.get('parent_company_id'):  #Update parent company if it exist
    #                 waka_parent_company = request.env['res.company'].sudo().search([('waka_company_id','=',data.get('parent_company_id'))],limit=1)
    #                 company_vals.update({'parent_id': waka_parent_company.id }) if waka_parent_company else False

    #             new_company = request.env['res.company'].sudo().create(company_vals) # Create the company record in Accounting system
    #             logging.info("******company created *********%s",new_company)
    #             check_invites = request.env['company.invites'].sudo().search([('waka_invited_company_id','=',data.get('invited_company_id')),('waka_invitee_company_name','=',data.get('company_name')),('waka_invitee_email','=',data.get('email')),('is_mapped','=',False)],limit=1)
    #             if check_invites:
    #                 invited_company = request.env['res.company'].sudo().search([('waka_company_id','=',check_invites.waka_invited_company_id)])
    #                 invited_company.external_stakeholder_ids = [(4,new_company.id,0)] #linking the invitee company as an external stakeholder
    #                 check_invites.is_mapped = True
    #                 logging.info("******invites mapped *********%s",check_invites)
    #             return {                                           # Return the success message with company details
    #                 'success':True,
    #                 'message': 'Company created successfully',
    #                 'accounting_company_id': new_company.id,
    #                 'accounting_new_company_name': new_company.name,
    #                 'code':200
    #             }

    #     except Exception as e:
    #         logging.exception("Error occurred while creating the company: %s", str(e))
    #         return {'error': str(e),'success':False}

    @http.route('/v1/invite/company', type='json', auth='public', methods=['POST'], website=False, cors='*', csrf=False)
    def invite_company(self, **kwargs):
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
            logging.info("*********** invite_company data ***************%s",data)
            if not data:
                return {'error': 'Data not found','code':404}
            invited_company = request.env['res.company'].sudo().browse(data.get('invited').get('accounting_company_id'))
            invited_user = request.env['res.users'].sudo().browse(data.get('invited').get('accounting_company_id'))
            if data.get('invitee').get('accounting_company_id'):
                invitee_company = request.env['res.company'].sudo().browse(data.get('invitee').get('accounting_company_id'))
                if not invitee_company:
                    return {'error': {'code': '404', 'message': 'The provided Invitee Accounting Company not found'}}
            else:
                company = data.get('company')   # company details
                waka_city = request.env['waka.city.master'].sudo().search([('wakatech_city_id','=',company.get('city_id'))],limit=1)
                waka_state = request.env['res.country.state'].sudo().search([('wakatech_state_id','=',company.get('state_id'))],limit=1)
                waka_country = request.env['res.country'].sudo().search([('wakatech_country_id','=',company.get('country_id'))],limit=1)
                company_vals = {
                'waka_company_id':company.get('invitee_company_id'),
                'name': company.get('company_name') +" - "+ waka_country.name,
                'company_name': company.get('company_name'),
                'company_local_name': company.get('company_local_name'),
                'company_ref_code': company.get('company_ref_code'),
                'contact_name': company.get('contact_name'),
                'email': company.get('email'),
                'phone': company.get('phone'),
                'zip': company.get('zip_code'),
                'country_id': waka_country.id if waka_country else False,
                'currency_id': waka_country.currency_id.id if waka_country else False,
                'state_id': waka_state.id if waka_state else False,
                'city_id': waka_city.id if waka_city else False,  #master to be synced
                'city': company.get('city_name'),
                'street': company.get('address_line_1'),
                'street2': company.get('address_line_2'),
                'website': company.get('website_address'),
                'eori_no': company.get('eori_no'),
                'export_reg_no': company.get('export_reg_no'),
                'import_reg_no': company.get('import_reg_no'),
                'inttra_id': company.get('inttra_id'),
                'scac_code': company.get('scac_code'),
                }
                if data.get('parent_company_id'):  #Update parent company if it exist
                    waka_parent_company = request.env['res.company'].sudo().search([('waka_company_id','=',data.get('parent_company_id'))],limit=1)
                    company_vals.update({'parent_id': waka_parent_company.id }) if waka_parent_company else False

                invitee_company = request.env['res.company'].sudo().create(company_vals) # Create the company record in Accounting system
                logging.info("******invitee_company created SUCCESS*********%s",invitee_company)

            if data.get('invitee').get('accounting_user_id'):
                invitee_user = request.env['res.users'].sudo().browse(data.get('invitee').get('accounting_company_id'))
                if not invitee_user:
                    return {'error': {'code': '404', 'message': 'The provided Invitee Accounting user not found'}}
            else:
                user = data.get('user')   # user details
                login_pass = request.env['api.keys.config'].sudo().search([('name','=','login_pass')], limit=1).secret_key
                # access = 'Accountant'   # setting default Accounting access Accountant for all newly created Admin
                access = request.env['res.groups'].sudo().search([('name', '=','Accountant')],limit=1).id
                # if user.get("role"):
                #     logging.info("*********** data.get(user_accounting_access) ***************%s",data.get("user_accounting_access"))
                #     access = request.env['res.groups'].sudo().search([('name', '=',user.get("role"))],limit=1).id   # if roles are provided in the request, accounting access will be updated

                accounting_dashboard_id = request.env['ir.actions.actions'].sudo().search([('name','=','Accounting Dashboard')], limit=1)   #map the Accounting Dashboard as Home action
                user_vals = {
                "name": user.get("contact_name"),
                "login": user.get("email"),
                "email": user.get("email"),
                "mobile": user.get("mobile"),
                "password":  login_pass,
                "company_id": invitee_company.id,
                "company_ids":[invitee_company.id],
                "lang": "en_US",
                "groups_id": [(4, access)],
                "wakatech_id":  user.get("waka_user_id"),
                "wechat_id": user.get("wechat_id"),
                "action_id":accounting_dashboard_id.id
                }

                invitee_user = request.env['res.users'].sudo().create(user_vals)
                logging.info(" ************** invitee_user created SUCCESS ************** %s",invitee_user.id)
                role = request.env['waka.roles'].sudo().search([('id', '=',int(user.get("role_id")))],limit=1)
                role.write({'user_ids': [(4,invitee_user.id,0)]}) if role else False   #linking the created user to the provided role
 
            external_stakeholders_data = [(4,invitee_company.id,0)] #linking the invitee company as an external stakeholder
            logging.info("----------external_stakeholders_data-------------%s",external_stakeholders_data)
            invited_company.write({'external_stakeholder_ids': external_stakeholders_data})

            logging.info("======= Invitee mapped ======")

            return {'success':True,'message': 'Company Invite Mapped successfully',
                'invitee_waka_user_id':invitee_user.wakatech_id,
                'invitee_waka_company_id':invitee_company.waka_company_id,
                'invitee_accounting_company_id': invitee_company.id,
                'invitee_accounting_user_id': invitee_user.id,
                'code':200}
        except Exception as e:
            logging.exception("Error occurred while mapping the Company Invitee: %s", str(e))
            return {'error': str(e),'success':False}
