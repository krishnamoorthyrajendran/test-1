from odoo import models, fields

class WakaJinrenMaster(models.Model):
    _name = 'jinren.master'
    _description = 'this master contains all the master data of Jinren E-invoicing'
    _rec_name = 'jinren_tenant_code'

    jinren_tenant_code = fields.Char("Tenant code")
    jinren_public_key = fields.Text("Public Key")
    jinren_private_key = fields.Text("Private Key")
    jinren_post_url = fields.Char("Jinren Post Url")
    dll_path = fields.Char("Dll path")
    bouncycastle_path = fields.Char("Bouncycastle file path")
    rsa_helper_path = fields.Char("RSAHelper file path")
    active = fields.Boolean(string="Active",default=False)

    jinren_history_url = fields.Char("Jinren History Url")


class WakaHJinrenAPILogs(models.Model):
    _name = 'jinren.api.logs'
    _description = 'this master contains API logs of Jinren E-invoicing'
    _rec_name = 'create_date'

    move_id = fields.Many2one("account.move", "Invoice")
    jinren_raw_data = fields.Text("Raw Data")
    public_xml = fields.Text("Public Key XML")
    encrypted_data = fields.Text("Encrypted Data")
    post_data = fields.Text("Data Posted")
    response_data = fields.Text("Response Data")
    status_code = fields.Char("Response status code")
    status = fields.Char("Status")
    error_remarks = fields.Char("Error Remarks")

    #history
    hist_raw_data = fields.Text("Raw data")
    hist_post_data = fields.Text("Data Posted")
    hist_response_data = fields.Text("Response Data")
    hist_status_code = fields.Char("Response status code")
    hist_status = fields.Char("History status")
    hist_error_remarks = fields.Char("Error Remarks")
