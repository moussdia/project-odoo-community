# -*- coding: utf-8 -*-

from odoo import fields, models, api


class LeadOpponent(models.Model):
    _name = 'crm.lead.opponent'

    name = fields.Char('Nom')
    function = fields.Char('Fonction')
    contact = fields.Char('Contact')
    lead_id = fields.Many2one('crm.lead', 'Lead')


class LeadAllies(models.Model):
    _name = 'crm.lead.allies'

    name = fields.Char('Nom')
    function = fields.Char('Fonction')
    contact = fields.Char('Contact')
    lead_id = fields.Many2one('crm.lead', 'Lead')


class LeadCustomerTeam(models.Model):
    _name = 'crm.lead.customer.team'

    name = fields.Char('Nom')
    function = fields.Char('Fonction')
    contact = fields.Char('Contact')
    lead_id = fields.Many2one('crm.lead', 'Lead')


class LeadManager(models.Model):
    _name = 'crm.lead.manager'
    _description = 'Personnes Dirigeantes'
    _rec_name = 'id'

    partner_id = fields.Many2one('res.partner', string='P. Dirigeante', required=True, help='Personne Dirigeante')
    power_of_decision = fields.Char(string='Pouvoir', required=True, help='Pouvoir de décision')
    lead_id = fields.Many2one('crm.lead', string="Personnes dirigeantes & pouvoir de décision",
                              default={'lead_id': lambda self, cr, uid, context: context.get(
                                  'lead_id', False), })

    visit_frequency = fields.Integer('FQ', help='Fréquence de visite')
    visit_frequency_period = fields.Selection([('day', 'jour(s)'),
                                               ('week', 'Semaine(s)'),
                                               ('month', 'Mois')], default='day', help='Temps de frequence de visite')
    need_to_have_lunch = fields.Selection([('yes', 'Oui'),
                                           ('no', 'Non')], default='yes', string='Déjeuner ?',
                                          help='Nécessité de déjeuner d’affaire', required=True,)

    business_lunch_frequency = fields.Integer('Fq déjeuner', help='Fréquence de déjeuner d’affaire')
    business_lunch_frequency_period = fields.Selection([('day', 'jour(s)'),
                                                        ('week', 'Semaine(s)'),
                                                        ('month', 'Mois')], default='day', help='Temps de fréquence')
    business_lunch_budget = fields.Integer('Budget dej.', help='Budget de déjeuner d’affaire', default=0)
    sponsor_name = fields.Char('Parrain', help='Nom du parrain du compte')
    monetary = fields.Selection([('eur', 'EUR'),
                                 ('usd', 'USD'),
                                 ('xof', 'XOF')], default='xof')
    type_of_maillage = fields.Many2one('mesh.plan', string='Type', required=True, )
    partner = fields.Char('Personne dirigeante')

