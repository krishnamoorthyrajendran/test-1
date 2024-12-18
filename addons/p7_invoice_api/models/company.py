import odoo
from odoo import api, models, tools, fields
import secrets
import string



class ResComapnyToken(models.Model):
    _inherit = 'res.company'

    token = fields.Char("Token")

    # fields created based on the Wakatech comapany creation data
    waka_company_id = fields.Char(string="Waka Company ID")
    company_local_name = fields.Char(string="Company Local Name")
    company_logo_uuid = fields.Char(string="Company Logo UUID")
    company_name = fields.Char(string="wakatech Company Name")
    company_ref_code = fields.Char(string="Company Reference Code")
    contact_name = fields.Char(string="Contact Name")
    eori_no = fields.Char(string="EORI Number")
    export_reg_no = fields.Char(string="Export Registration Number")
    from_invite = fields.Boolean(string="From Invite", default=False)
    import_reg_no = fields.Char(string="Import Registration Number")
    inttra_id = fields.Char(string="INTTRA ID")
    owned_by = fields.Char(string="Owned By")
    city_id = fields.Many2one('waka.city.master', string="city")
    scac_code = fields.Char(string="SCAC Code")
    taxpay_id = fields.Char(string="Taxpay ID")

    # fields created based on the Wakatech comapany based on External stakeholder invitation
    invited_company_id = fields.Many2one('res.company',string='Invited Company ID')
    invited_company_type = fields.Char(string='Invited Company Type')
    # invited_company_type_id = fields.Integer(string='Invited Company Type ID')
    # invited_company_type_lookup = fields.Char(string='Invited Company Type Lookup')
    invited_contact_name = fields.Char(string='Invited Contact Name')
    invited_country = fields.Char(string='Invited Country')
    # invited_country_flag = fields.Binary(string='Invited Country Flag')
    invited_email = fields.Char(string='Invited Email')
    invited_user_id = fields.Integer(string='Invited User ID')
    invitee_company_id = fields.Many2one('res.company',string='Invitee Company ID')
    invitee_company_name = fields.Char(string='Invitee Company Name')            #company_name

    invitee_contact_name = fields.Char(string='Invitee Contact Name')
    invitee_country = fields.Char(string='Invitee Country')

    # invitee_user_id = fields.Many2one('res.users',string='Invitee User ID')

    status = fields.Char(string='Status')

    # External stakeholders
    external_stakeholder_ids = fields.One2many('res.company','invitee_company_id',string="External Stakeholders")

    # Internal team members
    internal_team_members_ids = fields.One2many('res.users','company_id',string="Internal Team members")


    def create_token_bearer(self):
        # Define characters to use for generating the token
        characters = string.ascii_letters + string.digits
        # Generate a random token using the defined characters
        # token = ''.join(secrets.choice(characters) for _ in range(32))
        self.token =  ''.join(secrets.choice(characters) for _ in range(32))
        # return token


class API_Key_Config(models.Model):
    _name = 'api.keys.config'
    _description = 'This model used to store api keys'

    name = fields.Char("Token Type")
    secret_key = fields.Char("Secret Key")
