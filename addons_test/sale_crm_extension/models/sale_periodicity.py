# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime


class SalePeriodicity(models.Model):
    _name = 'sale.periodicity'
    _description = 'Période commerciale'
    _rec_name = 'name'

    name = fields.Char('Nom', required=True)
    start_date = fields.Date('Date début')
    end_date = fields.Date('Date fin')
    year_id = fields.Many2one('sale.year', 'Exercice commercial')
    state = fields.Selection([('draft', 'Brouillon'),
                              ('open', 'Ouvert'),
                              ('close', 'Fermé')], string="Statut",default='draft')

    def action_validate(self):
        """
        Open period
        :return:
        """
        for rec in self:
            rec.state = 'open'

    def action_close(self):
        """
        Close period
        :return:
        """
        for rec in self:
            rec.state = 'close'

    def action_draft(self):
        """
        Make to draft
        :return:
        """
        for rec in self:
            rec.state = 'draft'
