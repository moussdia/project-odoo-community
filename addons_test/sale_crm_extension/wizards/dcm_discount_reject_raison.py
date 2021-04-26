# -*- coding:utf-8 -*-

from odoo import fields, models, api, exceptions, _


class DcmDiscountRejectRaison(models.TransientModel):
    _name = 'dcm.discount.reject.raison'

    dcm_discount_note = fields.Text('Raison du réfus', required=True, track_visibility='onchange')

    def dcm_discount_reject_raison(self):
        orders = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        if orders:
            orders.write({'refuse_raison': self.dcm_discount_note
                         })
            orders.state = 'discount_chef_service_com_validated'

