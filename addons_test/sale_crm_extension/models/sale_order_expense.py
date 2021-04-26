# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrderExpense(models.Model):
    _name = 'sale.order.expense'
    _description = 'Charge d\'exploitation'
    _rec_name = 'name'

    name = fields.Char('Libellé')
    amount = fields.Float('Montant')
    order_id = fields.Many2one('sale.order', string="Bon de commande", default={'order_id': lambda self, cr, uid, context: context.get(
        'order_id', False), })


class SaleOrderExploitation(models.Model):
    _name = 'sale.order.exploitation'
    _description = 'Charge d\'exploitation'
    _rec_name = 'crm_id'

    name = fields.Many2one('charge.exploitation.nature', 'Nature exploitation')
    amount = fields.Float('Montant')
    crm_id = fields.Many2one('crm.lead', 'CRM')