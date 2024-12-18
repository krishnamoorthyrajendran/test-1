from odoo import models, fields, api
from odoo.exceptions import ValidationError
from cryptography.fernet import Fernet

class UserKey(models.Model):
    _name = 'user.key'
    _description = 'User Key'

    name = fields.Char(string="Name",required=True)
    key = fields.Char(string='Key',default=lambda self : self.update_key())


    @api.constrains('start_date', 'end_date')
    def _check_key_overlap(self):
        """Ensure that no other key is overlapping with the current key's start and end dates"""
        for record in self:
            overlapping_keys = self.search([
                ('id', '!=', record.id),  # Exclude the current record
                ('start_date', '<=', record.end_date),
                ('end_date', '>=', record.start_date),
            ])
            if overlapping_keys:
                raise ValidationError("The key date range overlaps with an existing key!")

class ResUser(models.Model):
    _inherit = "res.users"

    wakatech_id = fields.Char('Wakatech ID')
    wechat_id = fields.Char('Wechat ID')
    # contact_invite_id = fields.Many2one('res.users', string='Contact Invitor')
    company_id = fields.Many2one( 'res.company',string='Invitee Company ID')

class InviteeUser(models.Model):
    _name = "invitee.users"
    _description = 'Invitee users'


    name = fields.Char('Contact Name')
    email = fields.Char('Email')
    mobile = fields.Char('Mobile')
    contact_invite_id = fields.Many2one('res.users', string='Invited User')
    wechat_id = fields.Char('Wechat ID')
    company_id = fields.Many2one('res.company', string='company')
    wakatech_id = fields.Char('Wakatech ID')

