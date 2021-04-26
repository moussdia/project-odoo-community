# -*- coding:utf-8 -*-

from odoo import fields, models, api, exceptions, _
from collections import namedtuple
from calendar import monthrange
# from datetime import date
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import datetime


class RejectRaison(models.TransientModel):
    _name = 'reject.raison'

    note = fields.Text('Raison du réjet', required=True, track_visibility='onchange')

    def action_reject(self):
        res_partner = self.env['res.partner'].browse(self.env.context.get('active_id'))
        if res_partner:
            if res_partner.state == 'dcm':
                res_partner.write({
                    'refuse_raison': self.note
                })
            if res_partner.state == 'daf':
                res_partner.write({
                    'refuse_raison_daf': self.note
                })
            if res_partner.state == 'account':
                res_partner.write({
                    'refuse_raison_account': self.note
                })
            res_partner.action_refuse()
