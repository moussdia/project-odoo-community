# -*- coding:utf-8 -*-

from odoo import fields, models, api, exceptions, _


class DgaDiscountRejectRaison(models.TransientModel):
    _name = 'dga.discount.reject.raison'

    dga_discount_note = fields.Text('Raison du réfus', required=True, track_visibility='onchange')

    def dga_discount_reject_raison(self):
        orders = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        if orders:
            orders.write({'refuse_raison': self.dga_discount_note
                         })
            orders.state = 'discount_dcm_validated'

