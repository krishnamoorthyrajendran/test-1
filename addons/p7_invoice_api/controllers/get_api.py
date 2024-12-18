from odoo import http
from odoo.http import request
import json
import logging

class InvoiceMasterController(http.Controller):

    @http.route('/v1/get/payment_terms', type='http', auth='public', methods=['GET'], csrf=False, website=False, cors='*')
    def fetch_payment_terms(self, **kwargs):
        """
        API to fetch payment terms based on the given accounting_company_id in query parameters.
        - Returns both default and company-specific payment terms.
        :param kwargs: Query parameters (e.g., ?accounting_company_id=2)
        """
        try:
            # Get company_id from query params
            company_id = kwargs.get('accounting_company_id')

            if not company_id:
                logging.info("============ accounting_company_id is required ===============")
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'accounting_company_id is required'}),
                    headers={'Content-Type': 'application/json'}
                )

            # Convert company_id to integer
            company_id = int(company_id)

            # Search for payment terms
            payment_terms = request.env['account.payment.term'].sudo().search([
                '|',
                ('company_id', '=', False),   # Default payment terms
                ('company_id', '=', company_id)  # Company-specific payment terms
            ])

            # Prepare the response data
            result = [{'id': term.id,'name': term.name,'company_id': term.company_id.id if term.company_id else None,} for term in payment_terms]

            # Return the result as a JSON response
            return request.make_response(
                json.dumps({'success': True, 'payment_terms': result}),headers={'Content-Type': 'application/json'})

        except Exception as e:
            return request.make_response(json.dumps({'status': 'error', 'message': str(e)}),headers={'Content-Type': 'application/json'})


    @http.route('/v1/get/taxes', type='http', auth='public', methods=['GET'], csrf=False, website=False, cors='*')
    def fetch_taxes(self, **kwargs):
        """
        API to fetch taxes based on the given parameters.
        - Filters by `accounting_company_id`,`tax_type`, and `active` status if provided.
        :param kwargs: Query parameters (e.g., ?accounting_company_id=1&active=true&tax_type=sale)
        """
        try:
            # Extract parameters
            company_id = kwargs.get('accounting_company_id')
            active = kwargs.get('active')
            tax_type = kwargs.get('tax_type')

            if not company_id:
                logging.info("============ accounting_company_id is required ===============")
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'accounting_company_id is required'}),
                    headers={'Content-Type': 'application/json'}
                )
            
            if active is not None:                 # Convert `active` to boolean if provided
                active = active.lower() in ['true', '1']

            # Build search domain
            domain = []
            if company_id:
                domain.append(('company_id', '=', int(company_id)))
            if active is not None:
                domain.append(('active', '=', active))
            if tax_type:
                domain.append(('type_tax_use', '=', str(tax_type)))
            logging.info("============ fetch tax domain ===============%s",domain)
            # Fetch taxes from the tax master
            taxes = request.env['account.tax'].sudo().search(domain)

            # Prepare the response data
            result = [{
                'id': tax.id,
                'name': tax.name,
                'amount': tax.amount,
                'type_tax_use': tax.type_tax_use,  # e.g., sale, purchase, or none
                'active': tax.active,
                'company_id': tax.company_id.id if tax.company_id else None,
            } for tax in taxes]
            logging.info("=============no of taxes fetched==============%s",len(result))
            # Return the result as a JSON response
            return request.make_response(
                json.dumps({'status': 'success', 'taxes': result}),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            logging.info("============ error while fetching tax ===============")
            # Handle unexpected errors
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'}
            )

    # Tax groups available in odoo
    # "SGST","CGST","IGST","CESS","GST","Exempt","Nil Rated","Non GST Supplies","TCS","TDS"
    @http.route('/v1/compute/tax/amount/per/line', type='http', auth='public',methods=['GET'], csrf=False, website=False, cors='*')
    def compute_tax_amounts_api(self, **kwargs):
        """
        API to compute tax-excluded, tax-included, tax amount breakup based on the group .

        :param unit_price: unit price of the project
        :param quantity: quantity
        :param tax_ids: List of tax record IDs
        :param currency_id: Currency record ID
        :return: Dictionary with `total_excluded` and `total_included`
        """
        try: 
            def compute_tax_amounts(amount, tax_ids, currency,quantity):
                """
                Compute tax group, tax-excluded and tax-included amounts based on the total amount and taxes.

                :param quantity: Quantity of the prooduct
                :param unit_pice: Total amount (tax-inclusive or tax-exclusive depending on taxes configuration)
                :param tax_ids: Taxes applicable (list of tax records)
                :param currency: Currency record
                :return: Dictionary with `total_excluded` and `total_included`
                """
                try:

                    if not tax_ids:
                        return request.make_response(json.dumps({'total_excluded': amount,'total_included': amount,'tax_group_amount_per_line':False}),headers={'Content-Type': 'application/json'})


                    # Compute taxes            
                    taxes_res = tax_ids.compute_all(amount,currency=currency,quantity=quantity)
                    logging.info("========taxes_res=========%s",taxes_res)
                    
                    group_amount = {}
                    for sub_tax in taxes_res['taxes']:
                        sub_tax_id = request.env['account.tax'].sudo().browse(int(sub_tax['id']))
                        group_amount[sub_tax_id.tax_group_id.name] = group_amount.get(sub_tax_id.tax_group_id.name, 0) + sub_tax['amount']

                    return request.make_response(json.dumps({'total_excluded': taxes_res['total_excluded'],  # Amount before taxes
                                                            'total_included': taxes_res['total_included'],   # Amount after taxes
                                                            'tax_group_amount_per_line':group_amount         # Tax Group calculation (total amount for each group)
                                                            }),headers={'Content-Type': 'application/json'},status=201)
                
                except Exception as e:
                    logging.error(f"Error in compute_tax_amounts: {e}")
                    return request.make_response(
                        json.dumps({'error': 'An error occurred while computing tax amounts.', 'details': str(e)}),headers={'Content-Type': 'application/json'},status=500)
            
            unit_price = float(kwargs.get('unit_price', 0))
            quantity = float(kwargs.get('quantity', 1))
            tax_ids = kwargs.get('tax_ids')
            currency_id = int(kwargs.get('currency_id'))

            if not tax_ids or not currency_id:
                return request.make_response(json.dumps({'error': 'Tax IDs and Currency ID are required'}), headers={'Content-Type': 'application/json'}, status=400)
            
            logging.info("========calculate tax data=========%s",kwargs)
            # Fetch currency and tax records
            currency = request.env['res.currency'].sudo().browse(currency_id)
            tax_records = request.env['account.tax'].sudo().search([('id','in',eval(tax_ids))])
            
            # Compute tax amounts
            result = compute_tax_amounts(unit_price, tax_records, currency,quantity)
            return result
        
        except Exception as e:
            logging.error(f"Error in compute_tax_amounts: {e}")
            return request.make_response(
                json.dumps({'error': 'An error occurred while computing tax amounts.', 'details': str(e)}),headers={'Content-Type': 'application/json'},status=500)
