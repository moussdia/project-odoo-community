#-*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employe'

    name = fields.Char('NOM')
