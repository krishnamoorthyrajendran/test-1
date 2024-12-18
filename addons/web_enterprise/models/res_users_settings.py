# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api ,_


class ResUsersSettings(models.Model):
    _inherit = 'res.users.settings'

    homemenu_config = fields.Json(string="Home Menu Configuration", readonly=True)

class ResUsersForm(models.Model):
    _inherit = 'res.users'

    menus = fields.One2many('menu.line.item','menu_id',string="Menu Items")
    security_code = fields.Char()
class Menuslist(models.Model):
    _name = 'menu.list'
    _rec_name = 'name'
    _description = 'List of menu items in the Wakatech application'

    name = fields.Char(string="Menu Name")
    name_id = fields.Integer(string="Name id")
    url = fields.Char(string="Menu URL")
    logo = fields.Char(string="Logo") 
class Menulineitem(models.Model):
    _name = 'menu.line.item'
    _description = 'This master stores the sub-menuitems of each user'
    
    main_menu = fields.Char(string="Main Menu")
    main_menu_id = fields.Integer(string="Main Menu id")
    logo = fields.Char(string="Logo") 
    menu_id = fields.Many2one('res.users',string="Menus List")
    submenu_ids = fields.Many2many('menu.list','menu_list_line_item_rel', 'menu_line_item_id', 'menu_list_id',string="Submenus") 
    
    
    

class Change_password_for_wakatech(models.TransientModel):
    
    _inherit = 'change.password.user'
    
    
    @api.model_create_multi
    def create(self, vals):
        print("----vals--",vals)
        res = super(Change_password_for_wakatech,self).create(vals)
        
        for each in vals:
            if 'new_passwd' in each:
                user_obj = self.env['res.users'].browse(each.get('user_id'))
                if user_obj:
                    user_obj.security_code = each.get('new_passwd')
        return res
