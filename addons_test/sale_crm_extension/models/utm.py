# -*- coding: utf-8 -*-
from urllib.parse import urljoin

import werkzeug
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class UtmCampaignCategory(models.Model):
    _name = 'utm.campagne.category'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmMediaType(models.Model):
    _name = 'utm.media.type'
    _rec_name = 'name'

    name = fields.Char('Nom')


class UtmDisplayType(models.Model):
    _name = 'utm.display.type'
    _rec_name = 'name'

    media_type_id = fields.Many2one('utm.media.type', 'Type de média')
    name = fields.Char('Nom')


class UtmOutMediaType(models.Model):
    _name = 'utm.out.media.type'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmTarget(models.Model):
    _name = 'utm.target'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmTargetCategory(models.Model):
    _name = 'utm.target.category'

    target_id = fields.Many2one('utm.target', 'Cible')
    name = fields.Char('Nom')


class UtmTargetUnderCategory(models.Model):
    _name = 'utm.target.under.category'

    target_category_id = fields.Many2one('utm.target.category', 'Categorie')
    name = fields.Char('Nom')


class UtmPartner(models.Model):
    _name = 'utm.partner'

    name = fields.Char('Nom')
    description = fields.Char('description')


class UtmDiffusionType(models.Model):
    _name = 'utm.diffusion.type'

    name = fields.Char('Nom')
    media_type = fields.Many2one('utm.media.type', string='Type de média')
    description = fields.Char('description')


class UtmSuspect(models.Model):
    _name = 'utm.suspect'

    name = fields.Char('Nom')


class UtmInvestigation(models.Model):
    _name = 'utm.investigation'

    name = fields.Char('Nom')


class UtmQuestionsModelsLine(models.Model):
    _name = 'utm.questions.models.line'

    name = fields.Char('Nom')


class UtmQuestionsModels(models.Model):
    _name = 'utm.questions.models'

    name = fields.Char('Nom')


class SurveySuspect(models.Model):
    _name = 'survey.suspect'

    name = fields.Char('Nom')
    contact = fields.Char('Contact')
    contact2 = fields.Char('Téléphone')
    email = fields.Char('E-mail')
    address = fields.Char('Adresse')
    city = fields.Char('Ville')
    country = fields.Char('Pays', default='Côte d\'ivoire')
    function = fields.Char('Fonction')
    suspect_campaign_id = fields.Many2one('survey.campaign', 'Campagne')
    suspect_study_id = fields.Many2one('survey.survey', 'Etude')
    attribute = fields.Selection([('yes', 'Attribuer'),
                                  ('no', 'Non attribuer')], default='no')


class UtmCampaignExpense(models.Model):
    _name = 'utm.campaign.expense'

    nature_id = fields.Many2one('utm.campaign.nature.expense', 'Nature de dépense')
    amount = fields.Float('Budget estimatif')
    amount_realized = fields.Float('Dépense réalisée')
    state = fields.Selection([('draft', 'Planifier'),
                              ('done', 'Dépensé')])
    campaign_id = fields.Many2one('survey.campaign', 'Campagne')
    survey_campaign_id = fields.Many2one('survey.campaign', 'Campagne')


class UtmCampaignNature(models.Model):
    _name = 'utm.campaign.nature.expense'

    name = fields.Char('Nom')


class UtmCampaignNatureLogistic(models.Model):
    _name = 'utm.campaign.logistic'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmStrategy(models.Model):
    _name = 'utm.strategy'
    _rec_name = 'strategy'

    strategy = fields.Char('Strategie')
    description = fields.Char('Description')


class UtmCharacteristic(models.Model):
    _name = 'utm.characteristic'
    _rec_name = 'name'

    name = fields.Char('Nom')


class UtmSubCharacteristic(models.Model):
    _name = 'utm.sub.characteristic'
    _rec_name = 'name'

    characteristic_id = fields.Many2one('utm.characteristic', string='Caractéristique')
    name = fields.Char('Nom')


class UtmInfoCharacteristic(models.Model):
    _name = 'utm.info.characteristic'
    _rec_name = 'name'

    sub_characteristic_id = fields.Many2one('utm.sub.characteristic', string='Sous caractéristique')
    name = fields.Char('Nom')


class UtmRegion(models.Model):
    _name = 'utm.region'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmTown(models.Model):
    _name = 'utm.town'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')
    country_id = fields.Many2one('utm.country', string='Pays')


class UtmCommune(models.Model):
    _name = 'utm.commune'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')
    town_id = fields.Many2one('utm.town', string='Ville')


class UtmCsp(models.Model):
    _name = 'utm.csp'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmStudyLevel(models.Model):
    _name = 'utm.study.level'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmPersonality(models.Model):
    _name = 'utm.personality'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmCulture(models.Model):
    _name = 'utm.culture'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmCenterInterest(models.Model):
    _name = 'utm.center.interest'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmValue(models.Model):
    _name = 'utm.value'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmPurchaseFrequency(models.Model):
    _name = 'utm.purchase.frequency'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmReligion(models.Model):
    _name = 'utm.religion'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmCountry(models.Model):
    _name = 'utm.country'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')
    region_id = fields.Many2one('utm.region', 'Region')


class UtmAge(models.Model):
    _name = 'utm.age'
    _rec_name = 'name'

    name = fields.Char('Nom')
    description = fields.Char('Description')


class UtmStudy(models.Model):
    _name = 'utm.study'

    study = fields.Char('Libellé')


class UtmCampaignReport(models.Model):
    _name = 'utm.campaign.report'

    high_season = fields.Char('Saison haute')
    category = fields.Char('Categorie')

    # communication_and_marketing_actions = fields.Char('Lancement interne d\'un produit')
    # public_launch = fields.Char('Lancement public')
    # local_salon = fields.Char('Salon local')
    # target_mailing1 = fields.Char('Mailing cible 1')
    # target_mailing2 = fields.Char('Mailing cible 2')
    # price_increase = fields.Char('Augmentation tarifs')
    # national_fairs = fields.Char('Salons nationaux')
    # publicity = fields.Char('Pubicité')
    # public_relation = fields.Char('Relation publique')
    # gondola_head_promo = fields.Char('Promo tête de gondole')
    # sales_force_challenge = fields.Char('Challenge force de vente')

    def print_communication_marketing_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('sale_crm_extension.action_communication_marketing').report_action(self, data=data)

    # def init(self):
    #     """
    #     :return:
    #     """
    #     tools.drop_view_if_exists(self._cr, 'utm_campaign_report')
    #     self._cr.execute("""
    #                        CREATE OR REPLACE VIEW utm_campaign_report AS (
    #                        SELECT
    #                            row_number() OVER (PARTITION BY true) AS id,
    #                            COUNT(*) AS high_season,
    #                            utm_campagne_category AS category
    #                        FROM
    #                            public.utm_campaign AS m
    #                        GROUP BY utm_campagne_category
    #                        )""")


class ReportUtmCampaignReport(models.AbstractModel):
    _name = 'report.sale_crm_extension.report_utm_campaign_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
        }
