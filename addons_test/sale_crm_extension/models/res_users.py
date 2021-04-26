# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions


class Groups(models.Model):
    _inherit = "res.groups"
    _order = 'sequence'

    sequence = fields.Integer('Sequence')
