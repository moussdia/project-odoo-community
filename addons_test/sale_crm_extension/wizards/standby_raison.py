# -*- coding:utf-8 -*-

from odoo import fields, models, api, exceptions, _


class StandbyRaison(models.TransientModel):
    _name = 'standby.raison'

    note = fields.Text('Raison stand-by', required=True, track_visibility='onchange')

    def action_standby_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        if leads:
            leads.write({'standby_raison': self.note,
                         'is_standby': True if not leads.is_standby else False,
                         })


