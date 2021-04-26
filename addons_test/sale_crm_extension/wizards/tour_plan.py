# -*- coding: utf-8 -*-
import base64
from odoo import fields, models, api
from datetime import datetime


class TourPlan(models.TransientModel):
    _name = 'tour.plan.wizard'

    date_from = fields.Date('Date du')
    date_to = fields.Date('Au')

    def action_tour_plan_cron(self):
        print('bon')
        data = {
            'ids': self.ids,
            'model': self._name,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        print('data', data)
        return self.env.ref('sale_crm_extension.action_tour_plan').report_action(self, data=data)


class ReportTourPlan(models.AbstractModel):
    _name = 'report.sale_crm_extension.report_tour_plan'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        seller_users = []
        sellers = self.env['res.users'].search([])

        tour_plans = self.env['mail.activity'].search([
            ('date_deadline', '>=', data['date_from']),
            ('date_deadline', '<=', data['date_to']),
        ])

        for tour in tour_plans:
            docs.append(tour)

        for user in sellers:
            if user.has_group('sale_crm_extension.group_commercial'):
                seller_users.append(user)
        return {
            'date_from': datetime.strptime(data['date_from'], '%Y-%m-%d').strftime("%d %B %Y"),
            'date_to': datetime.strptime(data['date_to'], '%Y-%m-%d').strftime("%d %B %Y"),
            'records': docs,
            'seller_users': seller_users,
        }
