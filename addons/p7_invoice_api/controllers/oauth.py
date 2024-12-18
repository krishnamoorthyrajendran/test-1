# -*- coding: utf-8 -*-
from odoo import http,fields
from odoo.http import request, Response
import logging
import json
import werkzeug.wrappers
from .auth_jwt import JWT_
from collections import Counter
import base64,io
from odoo.modules.module import get_resource_path
from datetime import datetime, date,timedelta
import calendar
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.fields import Command

def access_token_validator(func):
    def wrapper(*args, **post):

        # if http.request.httprequest.method == 'OPTIONS':
        #     response = http.request.make_response("", headers=[
        #                                                     ('Access-Control-Allow-Headers', 'Content-Type, Authorization, access-token'),
        #                                                     ('Access-Control-Allow-Methods', 'POST, OPTIONS')])
        #     return response

        bearer_token = request.httprequest.headers.get('Authorization')
        # logging.info("Token --------------- %s",bearer_token)

        if bearer_token and bearer_token.startswith("Bearer "):
            # Split the bearer_token string by space and retrieve the bearer_token part
            bearer_token = bearer_token.split(" ")[1]
        else:
            error_json = json.dumps({'error': 'Bearer token is Missing/Incorrect'})
            return Response(error_json, status=401)

        if not bearer_token:
            error_json = json.dumps({'error': 'Bearer token is Missing/Incorrect'})
            return Response(error_json, status=401)

        if request.env.user.company_id.token != bearer_token:
            error_json = json.dumps({'error': 'Bearer token is Missing/Incorrect'})
            return Response(error_json, status=401)

        access_token = request.httprequest.headers.get('access-token')

        if not access_token:
            logging.info("Access token missing -------------------------")
            failure_json = json.dumps({'status':'Login Failed'})
            print("-------failure_json------",failure_json)
            return Response(failure_json, status=401)

        get_secret_key = request.env["api.keys.config"].sudo().search([],limit=1)

        if not get_secret_key:
            logging.info("Secret key not set for JWT -------------------------")
            failure_json = json.dumps({'status':'Login Failed'})
            return Response(failure_json, status=500)

        if get_secret_key and get_secret_key.secret_key:

            validate_access_token = JWT_(get_secret_key.secret_key).validate_access_token(str(access_token))

            # user = post['token_res'].get('user','')
            if validate_access_token[0] == "true":

                get_partner = request.env["res.partner"].sudo().search([('access_token','=',str(access_token))],limit=1)

                if get_partner:

                    post = {
                        "partner_id": validate_access_token[2].get('user',''),
                        "access_token": str(access_token)
                    }

                    return func(*args, **post)
                else:
                    logging.info("Access token not exist in the customer table -------------------------")
                    failure_json = json.dumps({'error':'Session Expired'})
                    return Response(failure_json, status=440)

            elif validate_access_token[1] == "token-expired":
                failure_json = json.dumps({'error':'Session Expired'})
                return Response(failure_json, status=440)
            else:
                error_json = json.dumps({'error': 'invalid-token'})
                return Response(error_json, status=500)

        logging.info("Secret key not set for JWT -------------------------")
        error_json = json.dumps({'status':'Login Failed.'})
        return Response(error_json, status=500)

    return wrapper
