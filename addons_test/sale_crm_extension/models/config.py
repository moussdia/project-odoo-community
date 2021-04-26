# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime


class EnterpriseSize(models.Model):
    _name = 'enterprise.size'
    _description = 'Taille de l\'entreprise'
    _rec_name = 'name'

    name = fields.Char('Nom')

    def onchange_case(self, name):
        result = {'value': {'name': str(name).upper()}}
        return result


class FormeJuridique(models.Model):
    _name = 'forme.juridique'
    _description = 'Forme juridique'
    _rec_name = 'name'

    name = fields.Char('Nom')


class DealOrigin(models.Model):
    _name = 'deal.origin'
    _description = 'Origine du deal'
    _rec_name = 'name'

    name = fields.Char('Nom')


class ActivitySector(models.Model):
    _name = 'activity.sector'
    _description = 'Secteur d’activité'
    _rec_name = 'name'

    name = fields.Char('Nom')


class LocalizationZone(models.Model):
    _name = 'localization.zone'
    _description = 'Zone géographique'
    _rec_name = 'zone'

    zone = fields.Char('Zone géographique')
    city = fields.Char('Ville')
    country_id = fields.Many2one('Pays')


class PrincipalActivity(models.Model):
    _name = 'principal.activity'
    _description = 'Activité principale'
    _rec_name = 'name'

    name = fields.Char('Nom')
    full_name = fields.Char('Nom complet')
    active = fields.Boolean('Activer', default=False)


class SectorActivity(models.Model):
    _name = 'sector.activity'
    _description = 'Secteur d’activités'
    _rec_name = 'name'

    name = fields.Char('Nom')
    full_name = fields.Char('Nom complet')
    active = fields.Boolean('Activer', default=True)


class ResPartnerGroup(models.Model):
    _name = 'res.partner.group'
    _description = 'Société appartenant à un group'
    _rec_name = 'name'

    name = fields.Char('Nom')
    partner_ids = fields.Many2many('res.partner', column1='partner_id', column2='group_id', string='Clients')
    active = fields.Boolean('Activer', default=True)


class CrmJob(models.Model):
    _name = 'crm.job'
    _description = 'Métier'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class PlanMaillage(models.Model):
    _name = 'mesh.plan'
    _description = 'Plan de maillage'
    _rec_name = 'name'

    name = fields.Char('Nom')


class ChargeExploitationNature(models.Model):
    _name = 'charge.exploitation.nature'
    _description = 'charge d\'exploitation'
    _rec_name = 'nature'

    nature = fields.Char('Nature charge d\'exploitation')


