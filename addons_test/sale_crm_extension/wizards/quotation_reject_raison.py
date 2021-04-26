# -*- coding:utf-8 -*-

from odoo import fields, models, api, exceptions, _


class QuotationRejectRaison(models.TransientModel):
    _name = 'quotation.reject.raison'

    note = fields.Text('Raison du réfus', required=True, track_visibility='onchange')

    def quotation_reject_raison(self):
        leads = self.env['sale.order'].browse(self.env.context.get('active_ids'))
        if leads:
            leads.write({'refuse_raison': self.note
                         })
            leads.state = 'draft'



