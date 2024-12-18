from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    scsb_id = fields.Char(string='SCSB ID')
    sop_sc_id = fields.Char(string='SOP SC ID')
    servicecharge_service_id = fields.Char(string='Service Charge Service ID')
    ts_ci_id = fields.Char(string='TS CI ID')    
    tsm_id = fields.Char(string='TSM ID')
    group_id = fields.Char(string='Group ID')
    service_master_id = fields.Char(string='Service Master ID')    
    port_type = fields.Char(string='Port Type')   
    type = fields.Char(string='Wakatech Type')
    is_sub_group = fields.Boolean(string='Is Sub Group')
    disabled = fields.Boolean(string='Disabled')    
    port_id = fields.Many2one('port.master', string="Port Type ")
    

    negotiated_rate = fields.Float(string="Negotiated Rate", digits=(15,3))
    service_qty = fields.Float(string="Service Quantity",digits=(15,3))
    sb_id = fields.Text(string='SB ID')
    hbl_number = fields.Text("HBL Number")
    shipment_mode = fields.Text(string='Shipment Mode')
    movement_id = fields.Many2one('movement.type', string="Movement Type")
    charge_item_id = fields.Many2one('product.template', string="Charge Item ID")  # product 
    charge_item = fields.Text(string='Charge Item')
    currency_id = fields.Many2one('res.currency', string="Currency")
    std_charge = fields.Float(string="STD Charge",digits=(15,3))
    # uom_id = 
    
    exp_charge = fields.Float(string="EXP Charge",digits=(15,3))
    tax = fields.Float(string="Tax")
    gst = fields.Float(string="GST")
    pst = fields.Float(string="PST")
    min_chargable_unit = fields.Float(string="Minimum Chargable Unit", digits=(15,3))
    min_base_charge =  fields.Float(string="Minimum Base Charge",digits=(15,3))
    unit_rate = fields.Float(string="Unit Rate",digits=(15,3))
    rendering_period = fields.Text("Rendering Period")
    eff_from_date = fields.Datetime(string="Effect From Date")
    eff_to_date = fields.Datetime(string="Effect To Date")
    notify_status = fields.Text(string='Notify Status')
    service_name_id = fields.Integer(string="Service Name ID")
    service_name = fields.Text(string='Service Name') 
    origin_port_id = fields.Many2one('port.master', string="Origin Port ")
    dest_port_id = fields.Many2one('port.master', string="Destination Port")
    amount = fields.Float(string="Amount", digits=(15,3))    
    processed_qty = fields.Float(string="Processed Quantity", digits=(15,3))
    final_amount = fields.Float(string="Final_Amount", digits=(15,3))
    billing_currency = fields.Text("Billing Currency")
    exchange_rate = fields.Float(string="Exchange Rate",digits=(15,3))
    comission_tax = fields.Float(string="Commission Tax", digits=(15,3))
    
    
     
    
    

    
