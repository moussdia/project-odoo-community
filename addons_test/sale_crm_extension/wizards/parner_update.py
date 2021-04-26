# -*- coding:utf-8 -*-
from urllib.parse import urljoin

import werkzeug

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class UpdateWizard(models.TransientModel):
    _name = 'update.wizard'

    ref_ids = fields.Many2many('res.partner', string='Contact')
    ref_update_ids = fields.Many2many('res.partner.update', 'res_partner_id_update_id', string='Update')

    def action_update_product(self):
        for rec in self:
            product_ids = self.env['product.template'].search([])
            for prod in product_ids:
                prod.write({
                    'invoice_policy': 'order',
                })

    def action_update(self):
        for rec in self:
            if rec.ref_update_ids:
                for ref_up in rec.ref_update_ids:
                    reference = ref_up.ref
                    if reference:
                        partner_ids = self.env['res.partner'].search([('ref', '=', reference)])
                        for partner in partner_ids:
                            partner.write({
                                'website': ref_up.website,
                                'street': ref_up.street,
                                'city': ref_up.city,
                                'mobile': ref_up.mobile,
                                'phone': ref_up.phone,
                                'partner_phone': ref_up.partner_phone,
                                'partner_mobile': ref_up.partner_mobile,
                                'email': ref_up.email,
                                'function': ref_up.function,
                                'partner_name': ref_up.partner_name,
                            })
                    else:
                        partner_ids = self.env['res.partner']
                        for partner in partner_ids:
                            partner.create({
                                'ref': ref_up.ref,
                                'name': ref_up.name,
                                'website': ref_up.website,
                                'street': ref_up.street,
                                'city': ref_up.city,
                                'mobile': ref_up.mobile,
                                'phone': ref_up.phone,
                                'partner_phone': ref_up.partner_phone,
                                'partner_mobile': ref_up.partner_mobile,
                                'email': ref_up.email,
                                'function': ref_up.function,
                                'partner_name': ref_up.partner_name,
                            })
