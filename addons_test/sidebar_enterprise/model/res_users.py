# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):

    _inherit = 'res.users'

    sidebar_visible = fields.Boolean("Afficher la barre latérale de l'application", default=True)
