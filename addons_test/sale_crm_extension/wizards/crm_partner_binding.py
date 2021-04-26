# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PartnerBinding(models.TransientModel):
    """
        Handle the partner binding or generation in any CRM wizard that requires
        such feature, like the lead2opportunity wizard, or the
        phonecall2opportunity wizard.  Try to find a matching partner from the
        CRM model's information (name, email, phone number, etc) or create a new
        one on the fly.
        Use it like a mixin with the wizard of your choice.
    """

    _inherit = 'crm.lead2opportunity.partner.mass'

    action = fields.Selection([
        ('create', 'Créer un nouveau client'),
        ('exist', 'Lier à un client existant'),
        ('nothing', 'Ne pas créer de lien avec un client')
    ], 'Related Customer', required=True)
