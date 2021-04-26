# -*- coding: utf-8 -*-
# from odoo import http


# class SaleCrmExtension(http.Controller):
#     @http.route('/sale_crm_extension/sale_crm_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_crm_extension/sale_crm_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_crm_extension.listing', {
#             'root': '/sale_crm_extension/sale_crm_extension',
#             'objects': http.request.env['sale_crm_extension.sale_crm_extension'].search([]),
#         })

#     @http.route('/sale_crm_extension/sale_crm_extension/objects/<model("sale_crm_extension.sale_crm_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_crm_extension.object', {
#             'object': obj
#         })
