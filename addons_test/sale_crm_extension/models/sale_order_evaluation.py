# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrderEvaluation(models.Model):
    _name = 'sale.order.evaluation'
    _description = 'Evaluation'
    _rec_name = 'name'

    name = fields.Char('Libellé')
    value = fields.Float('Valeur')
