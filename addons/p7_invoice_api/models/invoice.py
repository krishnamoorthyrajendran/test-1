from odoo import models, fields, api
from odoo.exceptions import UserError
import json
import logging

# pip install pycryptodome
# pip install pythonnet
import clr
import sys
import os
import requests

# public_key = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDGt3e4EhslYw6O1ZVinwBSL1H4Z6HiDrhUtawuewv2vgTOS4SRHvDxtz+4O+EH9IF126vwoJmxHmjLv08OUAhHEvdOZlyWTxAv39Mp72qUG6moNR+T9OxcAn3q2r0OauhhgcBb1TAny1cur9g5Nc5zuS83JzD2zKI/SNwxrFWIwIDAQAB"""
# private_key = """MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAMMa3d7gSGyVjDo7VlWKfAFIvUfhnoeIOuFS1rC57C/a+BM5LhJEe8PG3P7g74Qf0gXXbq/CgmbEeaMu/Tw5QCEcS905mXJZPEC/f0ynvapQbqag1H5P07FwCferavQ5q6GGBwFvVMCfLVy6v2Dk1znO5LzcnMPbMoj9I3DGsVYjAgMBAAECgYAR2y2fLkuylGVHFxMptQjwXSXlpEKMCO3KnXhEqF9zacj2iW8sANSK8HJdaVzCbN8d5b+dmmGw4h53zt8iWeMCe9dDOaLKBEEZWu4wOD5gQ5JdIQenUTbJLT6/5z/aznuyQLUFAW/F7as3vUr+Ge6YHK0SNdx9lJdj7Dd2vnSrcQJBANpzNLnqaPJ/8CA9DtA7t914vNthPOR+bY5ZlbyhCs8BeJw0Y4K/BVEN4UOME/GcaTCPKBa3hNmgl3Q7Bqn4Sd8CQQDkpF8MnY1pVY5WYRfsOZ+8WE4uwNWn2aUFoSOeY2PPoE/SNWSKpEUwMosQpk8LcVv1x5YvM7epWZUwq4KzJ8Q9AkEAnwZxIsq3nZlvWDi6uPJQVmTXryipaHl1DcS/kbL2qF2czLICoyKmHyxoiYDG4AOKO/RrLaZpivgyaUWzAzchpwJAAVxRDHwriULvE+iEAe3d23sTDAgtvU/4QW5SDfE9eNDVaMTUklaj6sOCPFkhA0prZ60GYcWHBET6NE3w+yvzaQJBAJmPRHq0DJWQjrJtmBJCtqnyeBnViTdTKBb4fC/kLzrHl9xczWx2Q67GE0EBMFrUDF3hJH2eZ3FFYH8I1O+OYVY="""



class AccountMoveInherited(models.Model):
    _inherit = 'account.move'   

    # jinren fields
    invoice_type = fields.Selection( selection=[('s', 'Paper Special Invoice'),
                                                ('c', 'Paper General Invoice'),
                                                ('x', 'Electronic Special Invoice'),
                                                ('p', 'Electronic General Invoice')
                                            ],string='Invoice Type',default='s' )
    machine_no = fields.Integer(string='Machine Number',default=0,help='The ticket machine number is mandatory. Defaults to 0. Pass the corresponding ticket machine number if there are multiple machines.')
    # payee_id= fields.Many2one('res.partner',string='Payee',domain=[('customer_rank', '>', 0)],help='Select the customer who is the payee.')
    checker_id = fields.Many2one('res.users',string='Checker',help='Select the user responsible for checking.')
    issuer_id = fields.Many2one('res.users',string='Issuer',help='Select the user issuing this document.')
    is_red = fields.Boolean(string='Is Red',default=False,help='Indicates whether the invoice is red.')
    blue_vat_code = fields.Char(string='Blue VAT Code',help='The VAT code of the blue invoice.')
    blue_vat_no = fields.Char(string='Blue VAT Number',help='The VAT number of the blue invoice.')
    red_notice_num = fields.Char(string='Red Notice Number',help='The notice number for the red invoice.')
    
    
    def action_open_jinren_logs(self):
        action = self.env['ir.actions.act_window']._for_xml_id('p7_invoice_api.action_jinren_api_logs')
        # Filter jinren.api.log records based on the move_id
        if self.id:
            domain = [('move_id', '=', self.id)]
            action['domain'] = domain
        return action


    def button_e_invoice(self):
        """Post Invoice to the Jinren system"""
        for record in self:
            if record.state != 'posted':   # Ensure the invoice is in the correct state before proceeding
                raise UserError("E-invoice cannot be generated in a %s state"%(record.state))
            
            # url = 'http://cloud.jinren.net/api/invoice/push-invoice'
            jinren = self.env['jinren.master'].search([('active','=',True)],limit=1)
            if not jinren:
                raise UserError("Please configure the API Keys in the Jinren Master")
            log_vals = {'move_id':self.id}
            url = jinren.jinren_post_url
            public_key = jinren.jinren_public_key
            # private_key = jinren.jinren_private_key
            # Path to your RsaHelper.dll and BouncyCastle.Crypto.dll
            dll_path = jinren.dll_path
            # dll_path = "/home/vaishnavi/HelloWorld/"
            # /home/vaishnavi/HelloWorld/BouncyCastle.1.8.9/lib/BouncyCastle.Crypto.dll

            # Add reference to BouncyCastle and RsaHelper DLLs
            clr.AddReference(os.path.join(dll_path, jinren.bouncycastle_path))     # 'BouncyCastle.1.8.9/lib/BouncyCastle.Crypto.dll'
            clr.AddReference(os.path.join(dll_path, jinren.rsa_helper_path))       #'RsaHelper.dll'

            # Import the RsaHelper class from the .NET namespace
            from JrQuickMini.Common import RsaHelper
            
            
            if self.company_id.jinren_demo_data:
                inv_data = {"InvoiceNo": record.name ,
                            "InvoiceType": "s",
                            "InvoiceDate": record.invoice_date or "2019-03-18",
                            "CustomerCode": "",
                            "CustomerName": record.partner_id.name or "上海金壬信息技术有限公司",
                            "TaxNo": record.partner_id.vat or "110101000000000",
                            "AddrTel": record.partner_id.phone or "测试地址电话0216585445",
                            "BankAcc": record.partner_id.bank_ids.acc_number if record.partner_id.bank_ids else False or "中国银行999999999",
                            "Remark": "测试备注",
                            "MachineNo": record.machine_no or 0,
                            "MobilePhone": record.partner_id.mobile or "13900000000",
                            "Email": record.partner_id.email or "admin@qq.com",
                            "Payee": record.partner_id.name or "张三",
                            "Checker": record.checker_id.name or "李四",
                            "Issuer": record.issuer_id.name or "王五",
                            "is_red": record.is_red,
                            "blue_vat_code" : record.blue_vat_code,
                            "blue_vat_no" : record.blue_vat_no,
                            "red_notice_num": record.red_notice_num,
                            "Rvc3": "",
                            "Rvc4": "",
                            "Rvc5": "",
                            "DetailList" :record.invoice_line_ids.mapped(lambda line: {
                            "ItemName": line.product_id.name,
                            "ItemSpec": line.name or "",
                            # "ItemUnit": line.unit_id.name or "个",
                            "Qty": line.quantity,
                            "Price": line.price_unit,
                            "Amt": line.price_subtotal,
                            "TaxRate": line.tax_ids[:1].amount / 100 if line.tax_ids else 0.0,
                            # "TaxAmt": line.price_tax,
                            "PriceIncludeTax": line.price_total,
                            "AmtIncludeTax": line.price_total,
                            "TaxCode": line.tax_ids[:1].description if line.tax_ids else "",
                            "ItemProperty": 0,
                            # "OrderNum": record.invoice_line_ids.index(line),  # Gets the index in the original recordset
                        })}
            else:
                inv_data = {"InvoiceNo": record.name ,
                            "InvoiceType": record.invoice_type,
                            "InvoiceDate": record.invoice_date,
                            "CustomerCode": "",
                            "CustomerName": record.partner_id.name ,
                            "TaxNo": record.partner_id.vat ,
                            "AddrTel": record.partner_id.phone ,
                            "BankAcc": record.partner_id.bank_ids.acc_number if record.partner_id.bank_ids else False ,
                            "Remark": "Posting Vat Invoice - " + record.name,
                            "MachineNo": 0,
                            "MobilePhone": record.partner_id.mobile ,
                            "Email": record.partner_id.email if record.partner_id.email else False,
                            "Payee": record.partner_id.name or record.partner_id.name if record.partner_id.name else False,
                            "Checker": record.checker_id.name or False,
                            "Issuer": record.issuer_id.name or False,
                            "is_red": record.is_red or False,
                            "blue_vat_code" : record.blue_vat_code,
                            "blue_vat_no" : record.blue_vat_no,
                            "red_notice_num": record.red_notice_num,
                            "Rvc3": "",
                            "Rvc4": "",
                            "Rvc5": "",
                            "DetailList" :record.invoice_line_ids.mapped(lambda line: {
                            "ItemName": line.product_id.name,
                            "ItemSpec": line.name or "",
                            # "ItemUnit": line.unit_id.name or "个",
                            "Qty": line.quantity,
                            "Price": line.price_unit,
                            "Amt": line.price_subtotal,
                            "TaxRate": line.tax_ids[:1].amount / 100 if line.tax_ids else 0.0,
                            # "TaxAmt": line.price_tax,
                            "PriceIncludeTax": line.price_total,
                            "AmtIncludeTax": line.price_total,
                            "TaxCode": line.tax_ids[:1].description if line.tax_ids else "",
                            "ItemProperty": 0,
                            # "OrderNum": record.invoice_line_ids.index(line),  # Gets the index in the original recordset
                        })}
            
            
            # inv_json = """{"InvoiceNo":"INV/2024/0000128","InvoiceType":"s","InvoiceDate":"2024-11-26","CustomerCode":"","CustomerName":"Abacus Freight","TaxNo":"110101000000000","AddrTel":"测试地址电话0216585445","BankAcc":"中国银行999999999","Remark":"测试备注","MachineNo":0,"MobilePhone":"13900000000","Email":"admin@qq.com","Payee":"Abacus Freight","Checker":"李四","Issuer":"王五","Rvc3":"","Rvc4":"","Rvc5":"","DetailList":[{"ItemName":"ADVANCED FILING RULE CHARGES","ItemSpec":"ADVANCED FILING RULE CHARGES","Qty":1.0,"Price":1.0,"Amt":1.0,"TaxRate":0.05,"PriceIncludeTax":1.06,"AmtIncludeTax":1.06,"TaxCode":"GST","ItemProperty":0},{"ItemName":"ADVANCED FILING RULE CHARGES","ItemSpec":"ADVANCED FILING RULE CHARGES","Qty":1.0,"Price":10.0,"Amt":10.0,"TaxRate":0.001,"PriceIncludeTax":10.01,"AmtIncludeTax":10.01,"TaxCode":"TCS @0.1% u/s 206C(1H): Sale of Goods","ItemProperty":0}]}"""
            inv_json = json.dumps(inv_data, ensure_ascii=False,default=str,separators=(',', ':'))
            logging.info("-------raw--------%s",inv_json,"\n\n")
            
            pub = RsaHelper.RsaPublicKeyToXml(public_key)
            log_vals.update({'jinren_raw_data':inv_json,'public_xml':pub})
            encrypted_data = RsaHelper.RsaEncrypt(inv_json, pub)

            # Decryption
            # private_pub = RsaHelper.RsaPrivateKeyToXml(private_key)
            # returnmsg = RsaHelper.RsaDecrypt(encrypted_data, private_pub)
            
            data ={"TenantCode":jinren.jinren_tenant_code, "Data":encrypted_data}
            logging.info(">>>>>>>>> data >>>>>>>%s",data)
            log_vals.update({'encrypted_data':encrypted_data,'post_data':data})
            api_log = self.env['jinren.api.logs'].create(log_vals)
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url,json=data, headers=headers)
            if response:
                logging.info("======response=======%s",response.json())
                api_log.write({'response_data':response.json(),'status_code':response.json()['statusCode'],'status':response.json()['succeeded'],'error_remarks':response.json()['errors']})
                record.message_post(body="The invoice has been Posted in to the Jinren system")
                if response.json()['succeeded']:
                    record.message_post(body="Jinren E-invoice status - Success")
                else:
                    record.message_post(body="Jinren E-invoice status - Failure, Please check the Jinren log")
            else:
                api_log.write({'error_remarks':'Response Not found'})

        return True

    def button_jinren_history(self):
        """Check Jinren History"""
        for record in self:
            jinren = self.env['jinren.master'].search([('active','=',True)],limit=1)
            if not jinren:
                raise UserError("Please configure the API Keys in the Jinren Master")
            api_log = self.env['jinren.api.logs'].search([('move_id','=',record.id)],limit=1,order='id desc')
            logging.info("======api_log=======%s",api_log)
            public_key = jinren.jinren_public_key
            # Path to your RsaHelper.dll and BouncyCastle.Crypto.dll
            dll_path = jinren.dll_path

            # dll_path = "/home/vaishnavi/HelloWorld/"
            # /home/vaishnavi/HelloWorld/BouncyCastle.1.8.9/lib/BouncyCastle.Crypto.dll

            # Add reference to BouncyCastle and RsaHelper DLLs
            clr.AddReference(os.path.join(dll_path, jinren.bouncycastle_path))   # 'BouncyCastle.1.8.9/lib/BouncyCastle.Crypto.dll'
            clr.AddReference(os.path.join(dll_path, jinren.rsa_helper_path))  #'RsaHelper.dll'

            # Import the RsaHelper class from the .NET namespace
            from JrQuickMini.Common import RsaHelper
            hist_raw_data =  {"InvoiceNo": record.name}
            hist_raw_json = json.dumps(hist_raw_data, ensure_ascii=False,default=str,separators=(',', ':'))
            logging.info("------History-raw--------%s",hist_raw_json)
            
            pub = RsaHelper.RsaPublicKeyToXml(public_key)
            
            encrypted_data = RsaHelper.RsaEncrypt(hist_raw_json, pub)

            url = jinren.jinren_history_url
            data = {"TenantCode":jinren.jinren_tenant_code,"Data":encrypted_data}
            api_log.write({'hist_raw_data':hist_raw_json,'hist_post_data':data}) if api_log else False
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url,json=data, headers=headers)
            logging.info("======Jinren History response=======%s",response.json())
            if response:
                api_log.write({'hist_response_data':response.json(),'hist_status_code':response.json()['statusCode'],'hist_status':response.json()['succeeded'],'hist_error_remarks':response.json()['errors']}) if api_log else False
                record.message_post(body="Jinren status checked")
                if response.json()['succeeded']:
                    
                    record.message_post(body="Jinren status - Success")
                else:
                    record.message_post(body="Jinren status - Failure, Please check the Jinren log")
            else:
                api_log.write({'hist_error_remarks':'Response Not found'}) if api_log else False
