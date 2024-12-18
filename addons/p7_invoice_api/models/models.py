# -*- coding: utf-8 -*-

from odoo import models, fields, api


class p7_invoice_api(models.Model):
    _name = 'p7_invoice_api.p7_invoice_api'
    _description = 'p7_invoice_api.p7_invoice_api'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100


class P7_res_company_inherit(models.Model):
    _inherit = "res.company"

    api_bearer_token = fields.Char(string="API Bearer Token", help="Bearer token for API authentication")
    jinren_demo_data = fields.Boolean(string="Use Demo data for Jinren",default=False)

class P7CurrencyInherited(models.Model):
    _inherit = "res.currency"
    # _rec_name = "wakatech_name"

    wakatech_id = fields.Integer(string="Wakatech id")
    wakatech_name = fields.Char(string="Wakatech Name")

class WakatechPortMaster(models.Model):
    _name = "port.master"
    _rec_name = "wakatech_name"
    _description = "This master carries all the port master data of Wakatech"

    wakatech_id = fields.Integer(string="Wakatech id")
    wakatech_name = fields.Char(string="Wakatech Name")
    active = fields.Boolean("Active" )

class MovementType(models.Model):
    _name = 'movement.type'
    _description = 'Movement Type'
    _rec_name = "wakatech_name"

    wakatech_id = fields.Char(string='Wakatech id')
    wakatech_name = fields.Char(string='Wakatech Name')

class ChargeItem(models.Model):
    _inherit = 'product.template'

    wakatech_charge_item_id = fields.Char(string='Wakatech Charge Item id')
    wakatech_charge_item = fields.Char(string='Wakatech Charge Item')


class AccountMove(models.Model):
    _inherit = 'account.move'

    shipping_invoice = fields.Boolean("Shipping Invoice", default=False )

class ResPartner(models.Model):

    _inherit = 'res.partner'

    wakatech_id = fields.Char(string='Wakatech id')

class ResCountry(models.Model):

    _inherit = 'res.country'

    wakatech_country_id = fields.Char(string='Wakatech id')


class ResCountryState(models.Model):

    _inherit = 'res.country.state'

    wakatech_state_id = fields.Char(string='Wakatech id')
    wakatech_state = fields.Char(string='Wakatech State Name')

class ComapnyInvites(models.Model):
    _name = 'company.invites'
    _description = 'This table is used to store the company invite information'

    waka_invited_company_id = fields.Char("Waka Invited Company ID")
    waka_invitee_company_name = fields.Char("Waka Invitee Company Name")
    waka_invitee_email = fields.Char("Waka Invitee Email")
    waka_invitee_contact_name = fields.Char("Waka Invitee Contact Name")
    is_mapped = fields.Boolean("Is Mapped into the company?",default=False)
