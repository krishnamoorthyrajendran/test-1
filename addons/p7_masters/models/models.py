# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class p7_masters(models.Model):
#     _name = 'p7_masters.p7_masters'
#     _description = 'p7_masters.p7_masters'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

