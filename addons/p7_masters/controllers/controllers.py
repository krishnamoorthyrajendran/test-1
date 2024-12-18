# -*- coding: utf-8 -*-
# from odoo import http


# class P7Masters(http.Controller):
#     @http.route('/p7_masters/p7_masters', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/p7_masters/p7_masters/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('p7_masters.listing', {
#             'root': '/p7_masters/p7_masters',
#             'objects': http.request.env['p7_masters.p7_masters'].search([]),
#         })

#     @http.route('/p7_masters/p7_masters/objects/<model("p7_masters.p7_masters"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('p7_masters.object', {
#             'object': obj
#         })

