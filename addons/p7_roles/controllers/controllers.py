from odoo import http
from odoo.http import request,Response
import json
import logging

class RestAPI(http.Controller):

    # Fetch Data with domain and fields
    @http.route('/v1/restapi/object/<string:object>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_records(self, object, **kwargs):
        try:
            params = request.params
            logging.info("======params======%s",params)
            # Parse domain and fields from query parameters
            domain = params.get('domain')  # Expecting domain as a JSON string in query params

            fields = params.get('fields')   # Expecting fields as a JSON array in query params
            logging.info("======fields======%s",fields)
            logging.info("======type,domain======%s%s",type(domain),domain)
            # Access the model and search records with the given domain and fields
            model = request.env[object].sudo()
            records = model.search_read(eval(domain), eval(fields))
            logging.info("__________No of records through search read________%s",len(records))


            return Response(json.dumps({'status': 'success', 'data': records}), content_type='application/json', status=200)

        except Exception as e:
            logging.info("======error in fetching records through restAPI=====")
            return Response(json.dumps({'status': 'error', 'message': str(e)}), content_type='application/json', status=500)
