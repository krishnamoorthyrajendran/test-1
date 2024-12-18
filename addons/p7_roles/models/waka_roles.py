from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.http import request
import logging

class WakaRoles(models.Model):
    _name = 'waka.roles'
    _description = 'Waka Roles'
    _rec_name = 'role_name'
    _sql_constraints = [
        ('unique_role_name_company_id', 'UNIQUE(role_name, company_id)', 'The role name must be unique per company.')
    ]

    role_name = fields.Char(string='Role Name', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    accounting_group = fields.Many2one('res.groups', string='Accounting Group')
    user_ids = fields.Many2many('res.users', 'waka_groups_users_rel', 'waka_group_id', 'user_id', string="Users in Role")

    @api.constrains('role_name', 'company_id')
    def _check_unique_role_name_company(self):
        for record in self:
            duplicate = self.search([
                ('role_name', '=', record.role_name),
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError("The role name must be unique within the same company.")

class ResUsers(models.Model):
    _inherit = 'res.users'

    waka_group_id = fields.Many2one('waka.roles', string='Waka Group')
    is_waka_admin = fields.Boolean(string="Is Wakatech Admin", default=False)
    admin_company_ids = fields.Many2many('res.company', 'user_admin_company_rel', 'user_id', 'company_id', string="Wakatech Admin Companies")

    def set_groups_from_roles(self,cids=False):
        accounting_company_id = request.env['res.company'].sudo().search([('id','in',cids)],limit=1)
        logging.info("====== accounting_company_id============%s",accounting_company_id)

        if accounting_company_id:
            accounting_role = request.env['waka.roles'].sudo().search([('company_id','=',accounting_company_id.id),('user_ids','in',self.id)],limit=1)
            logging.info("====== accounting_role00000000============%s",accounting_role)
            if accounting_role:
                acc_groups = request.env['res.groups'].sudo().search([('category_id.name','in',['Accounting','Invoicing'])])
                self.write({"groups_id": [(3, user_id, 0) for user_id in acc_groups.ids]+ [(4, accounting_role.accounting_group.id, 0)],})

class ResGroups(models.Model):
    _inherit = 'res.groups'

    is_waka_group = fields.Boolean(string="Waka group")

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        """
        Based on the selected companies (cids),
        calculate the roles to enable.
        A role should be enabled only when it applies to all selected companies.
        """
        result = super(IrHttp, self).session_info()
        logging.info(">....................logging in........................")
        accounting_role = request.env['waka.roles'].sudo().search([('user_ids','in',self.env.user.id)],limit=1)
        if accounting_role:
            logging.info(">............accounting_role...........%s",accounting_role)
            cids_str = request.httprequest.cookies.get("cids", str(self.env.company.id))
            cids = [int(cid) for cid in cids_str.split(",")]
            self.env.user.set_groups_from_roles(cids)
        else:
            if self.env.user.is_waka_admin and self.env.company.id in self.env.user.admin_company_ids:
                logging.info(">===========Admin login==============")
                accountant_access = request.env['res.groups'].sudo().search([('name', '=','Accountant')],limit=1)
                acc_groups = request.env['res.groups'].sudo().search([('category_id.name','in',['Accounting','Invoicing'])])
                self.env.user.groups_id = [(3, user_id, 0) for user_id in acc_groups.ids]+ [(4, accountant_access.id, 0)]
        return result
