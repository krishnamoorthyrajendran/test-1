from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('approve', 'To Approve'),('posted',)],ondelete={'approve': 'cascade'})


    def send_approval(self):
        for rec in self:
            rec.state = 'approve'

    
    def action_approve(self):
        for rec in self:
            rec.action_post()

    def action_reject(self):
        for rec in self:
            rec.state = 'draft'