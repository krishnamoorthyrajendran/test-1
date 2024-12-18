# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import logging
import json
from datetime import datetime
import logging


class ProductApi(http.Controller):

    @http.route(['/v1/create/product','/v1/update/product'], type='json', auth='public', methods=['POST', 'PUT'])
    def create_or_update_product(self, **params):
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
            logging.info("*********** product data ***************%s",data)
            if not data:
                return {'error': 'Data not found','code':404}
            
            name = data.get('name')
            product_id = data.get('product_id')
            type = data.get('product_type', 'service')
            list_price = data.get('price', 0.0)
            category_name = data.get('category_name')
            default_code = data.get('default_code')
            income_id = data.get('income_id')
            expense_id = data.get('expense_id')
            if product_id:  # existing product update
                existing_product = request.env['product.template'].sudo().browse(product_id)
                if not existing_product.exists():
                    return {'error': f'Product with ID {product_id} not found.'}

                # Ensure the user has access to modify this product
                existing_product.sudo().write({
                    'name': name,
                    'type': type,
                    'list_price': list_price,
                    'default_code': default_code,
                    'property_account_income_id': income_id,
                    'property_account_expense_id': expense_id
                })
                logging.info('Existing product =========================%s',existing_product)
                return {'success':True,'message': 'Product Updated Successfully','existing_product_id':existing_product.id,'code':200}
            else:  # Create new product
                if not name or not category_name:
                    return {'error': 'Product name or Product category name is missing'}

                category = request.env['product.category'].sudo().search([('name', '=', category_name)])
                if not category.exists():
                    return {'error': f'Category with Name {category_name} does not exist.'}

                existing_product = request.env['product.template'].sudo().search([('name', '=', name),('categ_id', '=', category.id)])
                if existing_product:
                    return {
                        'error': f'A product with the name "{name}" already exists in the category "{category_name}".','product_id':existing_product.id}

                # Create new product
                product = request.env['product.template'].sudo().create({
                    'name': name,
                    'type': type,
                    'list_price': list_price,
                    'categ_id': category.id,
                    'default_code': default_code,
                    'property_account_income_id': income_id,
                    'property_account_expense_id': expense_id
                })
                return {'success':True,'message': 'Product Created Successfully','product_id':product.id,'code':200}
       
        except Exception as e:
            return {'error': f'An unexpected error occurred: {str(e)}'}