# -*- coding:utf-8 -*-

from odoo import fields, models, api, exceptions, _


class DiscountRejectRaison(models.TransientModel):
    _name = 'discount.reject.raison'

    discount_note = fields.Text('Raison du réfus', required=True, track_visibility='onchange')

    def discount_reject_raison(self):
        orders = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        if orders:
            orders.write({'refuse_raison': self.discount_note
                         })
            orders.state = 'submitted'

