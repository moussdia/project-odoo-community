# -*- coding: utf-8 -*-
import base64
import string
import webbrowser

from odoo import fields, models, tools, api


class ProductivitePerformanceView(models.Model):
    _name = 'productivite.performance.view'

    number_of_customer_visits = fields.Float('Nombre de visites clients')
    number_of_cases = fields.Float('Nombre d’affaires', help="Nombre d’affaires")
    big_customer = fields.Float('Gros client')
    medium_customer = fields.Float('Moyen client')
    small_customer = fields.Float('Petit client')

    number_of_new_clients = fields.Float('Nb nouveaux clients', help="Nombre de nouveaux clients")
    number_of_prospects = fields.Float('Nb prospects', help="Nombre de prospects")
    ca_of_new_clients = fields.Float('C.A nouveaux clients', help="Chiffre d’Affaires des nouveaux clients")
    average_amount_of_business = fields.Float('Mt moyen affaires', help="Montant moyen des affaires")
    number_of_active_clients = fields.Float('Nb clients actifs', help="Nombre de clients actifs")
    rate_of_transformation_of_project_into_business = fields.Float('Taux de transformation',
                                                                   help="Taux de transformation d’un projet en affaires")

    big_customer_docs = fields.Integer('Nombre de visites par gros client')
    middle_customer_docs = fields.Integer('Nombre de visites par moyen client')
    small_customer_docs = fields.Integer('Nombre de visites par petit client')
    number_of_prospecting_visits = fields.Integer('Nombre de visites de prospection')
    amount_of_unpaid_bills = fields.Float('Montant des impayés')
    number_of_disputes = fields.Integer('Nombre de litiges')

    # number_of_customer_visits = fields.Float('Nombre de visites clients')
    # difference_between_number_of_visits_achievements = fields.Float('Ecart nbre visite', help="Écart entre nombre de visites et réalisations")
    # number_of_customers_per_segment = fields.Float('Nb clients par segment', help="Nombre de clients par segment (ABC par exemple)")
    # number_of_cases = fields.Float('Nombre d’affaires', help="Nombre d’affaires")
    # number_of_promotional_actions = fields.Float('Nb d’actions pro', help="Nombre d’actions promotionnelles")
    # weight_of_promotions_in_total_turnover = fields.Float('Poids promotions C.A', help="Poids des promotions dans le total du Chiffre d’Affaires")
    # settlement_period = fields.Date('Délai règlement', help="Délai de règlement")
