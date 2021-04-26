# -*- coding: utf-8 -*-
from urllib.parse import urljoin

import werkzeug
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    suspect = fields.Char('Suspect')
    template_id = fields.Many2one('survey.template', related='survey_id.template_id', string='Template', store=True)

    # @api.onchange('template_id')
    # def _get_user_template_questions(self):
    #     for rec in self:
    #         ids_question = []
    #         for record in rec.template_id.question_ids:
    #             ids_question.append(record.id)
    #             rec.user_input_line_ids = [(6, 0, ids_question)]
    #             print('rec.user_input_line_ids', rec.user_input_line_ids)

    def action_submit(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_validate(self):
        for rec in self:
            rec.state = 'done'


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    template_id = fields.Many2one('survey.template', related='survey_id.template_id', string='Template', store=True)
    survey_id = fields.Many2one('survey.survey', string='Etude')


class SurveyTemplate(models.Model):
    _name = 'survey.template'

    name = fields.Char('Nom')
    description = fields.Char('Description')
    survey_template_id = fields.Many2one('survey.survey', string='Etude')
    question_ids = fields.One2many('survey.question', 'template_id', string='Question')


class SurveyUserInputLineInherit(models.Model):
    _inherit = 'survey.user_input.line'

    partner_id = fields.Many2one('res.partner', string='Partnenaire')
    suspect = fields.Char('Suspect')
    email = fields.Char(string='Email')
    template_id = fields.Many2one('survey.template', related='survey_id.template_id', string='Template', store=True)

    @api.onchange("template_id")
    def onchange_get_country_id(self):
        if self.template_id:
            return {'domain': {'question_id': [('template_id', '=', self.template_id.id)]}}
        else:
            return {'domain': {'question_id': [('template_id', '=', False)]}}


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    state = fields.Selection(selection=[('draft', 'Initialisation'),
                                        ('open', 'Collecte'),
                                        ('analyse', 'Analyse'),
                                        ('recommandation', 'Recommandation'),
                                        ('closed', 'Finish')], string="Survey Stage", default='draft',
                             required=True, group_expand='_read_group_states')
    client_segment = fields.Selection([('b2b', 'B2B'),
                                       ('b2c', 'B2C'),
                                       ('b2b-b2c', 'B2B-B2C')], string='Segment clientèle')

    strategy_id = fields.Many2one('utm.strategy', 'Strategie')
    start_date = fields.Date('Date de début')
    and_date = fields.Date('Date de fin')
    editor = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)

    utm_study_id = fields.Many2one('utm.study', 'Etude')
    utm_study = fields.Char('Etude', related='utm_study_id.study')
    branch_activity_id = fields.Many2one('res.partner.industry', 'Secteur d\'activité')
    company_size_id = fields.Many2one('enterprise.size', 'Taille de l\'entreprise')
    number_employees = fields.Integer('Nombre de salariés : ', compute='get_total_number_of_employees')
    volume_consumed = fields.Float('Volumes consommés')
    internationalized_degree = fields.Float('Degré d\'internationalisation')
    activity_type = fields.Selection([('mono', 'Mono Activité'),
                                      ('multi', 'Multi Activité')], string='Type d\' Activité')
    centralisation_type = fields.Selection([('centralisation', 'Centralisés'),
                                            ('decentralisation', 'Décentralisés')],
                                           string='Degré de centralisation des achats')
    searched_advantage = fields.Selection([('prix', 'Prix'),
                                           ('securite', 'Sécurité'),
                                           ('flexibilite', 'Flexibilité')], string='Avantage recherché')
    weight_function = fields.Selection([('faible', 'Faible'),
                                        ('moyen', 'Moyen'),
                                        ('eleve', 'Elévé')], string='Poids de la fonction technique')
    price_importance = fields.Selection([('faible', 'Faible'),
                                         ('moyen', 'Moyen'),
                                         ('eleve', 'Elévé')], string='Importance accordée au facteur prix')
    sector = fields.Selection([('public', 'Public'),
                               ('prive', 'Privé')], string='Secteur')
    company_turnover = fields.Float('Chiffre d’affaire de la société')
    monetary = fields.Selection([('eur', 'EUR'),
                                 ('usd', 'USD'),
                                 ('xof', 'XOF')], default='xof')
    number_man = fields.Integer('Nombre d’hommes')
    number_woman = fields.Integer('Nombre de Femmes')
    capital = fields.Float('Capital')
    region_id = fields.Many2one('utm.region', 'Région')
    country_id = fields.Many2one('utm.country', 'Pays')
    age_id = fields.Many2many('utm.age', 'survey_id', 'age_id', string='Age')
    town_id = fields.Many2one('utm.town', 'Ville')
    commune_id = fields.Many2one('utm.commune', 'Commune')
    gender = fields.Selection([('masculin', 'Masculin'),
                               ('feminin', 'Feminin')], string='Genre')
    sex = fields.Selection([('masculin', 'M'),
                            ('feminin', 'F'),
                            ('ms', 'M/F')], string='Sexe')
    number_of_person = fields.Integer('Nb de personne au foyer')
    income = fields.Integer('Revenus')
    csp_id = fields.Many2one('utm.csp', string='Catégorie socio-professionnelle')
    familial_status = fields.Selection([('marie', 'Marié(e)'),
                                        ('celibat', 'Célibataire'),
                                        ('divorce', 'Divorcé(e)')], string='Situation matrimoniale')
    education_level_id = fields.Many2one('utm.study.level', string='Niveau d\'étude')
    life_style = fields.Selection([('bas', 'Bas'),
                                   ('moyen', 'moyen'),
                                   ('eleve', 'Elévé')], string='Niveau de vie')
    personality_id = fields.Many2one('utm.personality', string='Personnalité')

    segmentation = fields.Char('Segmentation')
    target = fields.Char('Ciblage')
    positioning = fields.Char('Positionnement')
    mix_marketing = fields.Char('Mix marketing')
    study_suspect_ids = fields.One2many('survey.suspect', 'suspect_study_id', string='Suspect',
                                        domain=[('attribute', '=', 'no')])
    template_id = fields.Many2one('survey.template', string='Template')

    culture_id = fields.Many2one('utm.culture', 'Culture')
    nationality = fields.Char('Nationalité')

    need = fields.Char('Besoin')
    reference = fields.Char('Réference')
    center_of_interest_id = fields.Many2one('utm.center.interest', 'Centre d\'interêt')

    value_id = fields.Many2one('utm.value', 'Valeur')
    conviction = fields.Char('Conviction')
    center_of_interest2_id = fields.Many2one('utm.center.interest', 'Centre d\'interêt')

    purchase_frequency_id = fields.Many2one('utm.purchase.frequency', 'Fréquence d\'achat')
    consumption_habit = fields.Char('Habitude de consommation')
    level_of_live = fields.Selection([('bas', 'Bas'),
                                      ('moyen', 'moyen'),
                                      ('eleve', 'Elévé')], string='Niveau de vie')
    use = fields.Char('Utilisation')
    religion_id = fields.Many2one('utm.religion', 'Religion')

    @api.onchange("region_id")
    def onchange_get_country_id(self):
        if self.region_id:
            return {'domain': {'country_id': [('region_id', '=', self.region_id.id)]}}
        else:
            return {'domain': {'country_id': [('region_id', '=', False)]}}

    @api.onchange("country_id")
    def onchange_get_town_id(self):
        if self.country_id:
            return {'domain': {'town_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'town_id': [('country_id', '=', False)]}}

    @api.onchange("town_id")
    def onchange_get_commune_id(self):
        if self.town_id:
            return {'domain': {'commune_id': [('town_id', '=', self.town_id.id)]}}
        else:
            return {'domain': {'commune_id': [('town_id', '=', False)]}}

    @api.onchange('template_id')
    def _get_template_questions(self):
        for rec in self:
            ids_question = []
            for record in rec.template_id.question_ids:
                ids_question.append(record.id)
                rec.question_and_page_ids = [(6, 0, ids_question)]

    @api.depends('number_man', 'number_woman')
    def get_total_number_of_employees(self):
        for rec in self:
            rec.number_employees = rec.number_man + rec.number_woman
            return rec.number_employees


class SurveyCampaign(models.Model):
    _name = 'survey.campaign'
    _rec_name = 'name'

    name = fields.Char('Nom')
    campaign_advanced = fields.Integer('Etat d’avancement')
    start_date = fields.Date('Date de début')
    and_date = fields.Date('Date de fin')
    percentage = fields.Char('%', default="%")
    media_plan = fields.Selection([('media', 'Média'),
                                   ('out_media', 'Hors Média')], string='Type de communication')
    type_of_media_id = fields.Many2one('utm.media.type', string='Canal')
    type_of_out_media_id = fields.Many2one('utm.out.media.type', string='Type Plan média')
    target_media_id = fields.Many2many('utm.display.type', string='Support')
    diffusion_type_id = fields.Many2many('utm.diffusion.type', string='Type de diffusion')
    location = fields.Char('Lieu')
    logistics = fields.Many2many('utm.campaign.logistic', 'campaign_logistic_rel', 'campaign_id', 'logistic_id',
                                 string='Logistiques')
    products_ids = fields.Many2many('product.template', 'product_campaign_rel', 'product_id', 'campaign_id',
                                    string='Produits/Sce')
    partner_ids = fields.Many2many('utm.partner', 'survey_partner_campaign_rel', 'partner_id', 'campaign_id',
                                   string='Partenaire')
    expense_ids = fields.One2many('utm.campaign.expense', 'survey_campaign_id', string='Dépenses')
    amount_total = fields.Float('Total', compute='_amount_total', store=True)
    total_spending = fields.Float('Dépense totale', compute='_get_total_spending', store=True)
    status = fields.Selection([('draft', 'Brouillon'),
                               ('planned', 'Planifier'),
                               ('executed', 'Executer'),
                               ('checked', 'Corriger'),
                               ('done', 'Terminer')], default='draft', string='Etat')
    recipients_mails = fields.Char('Diffusion email', compute='_get_recipients_mails')
    target_id = fields.Many2one('utm.target', string='Cible')
    target_category_id = fields.Many2one('utm.target.category', string='Categorie')
    target_under_category_id = fields.Many2one('utm.target.under.category', string='Sous categorie')
    survey_suspect_ids = fields.One2many('survey.suspect', 'suspect_campaign_id', string='Suspect',
                                         domain=[('attribute', '=', 'no')])
    turnover = fields.Float('Chiffre d\'affaire')
    margin = fields.Float('Marge bruite commerciale')
    opex = fields.Float('OPEX', default='')

    def action_submit(self):
        for rec in self:
            rec.status = 'planned'

    def action_planned(self):
        for rec in self:
            rec.status = 'executed'

    def action_executed(self):
        for rec in self:
            rec.status = 'checked'

    def action_checked(self):
        for rec in self:
            rec.status = 'done'
            rec._get_recipients_mails()
            rec.send_notification('campaign_done_send_mail')

    def action_return(self):
        for rec in self:
            if rec.status == 'planned':
                rec.status = 'draft'
            if rec.status == 'executed':
                rec.status = 'planned'
            if rec.status == 'checked':
                rec.status = 'executed'

    @api.onchange("target_category_id")
    def onchange_target_category_id(self):
        if self.target_category_id:
            return {'domain': {'target_under_category_id': [('target_category_id', '=', self.target_category_id.id)]}}
        else:
            return {'domain': {'target_under_category_id': [('target_category_id', '=', False)]}}

    @api.onchange("target_id")
    def onchange_target_id(self):
        if self.target_id:
            return {'domain': {'target_category_id': [('target_id', '=', self.target_id.id)]}}
        else:
            return {'domain': {'target_category_id': [('target_id', '=', False)]}}

    @api.onchange("type_of_media_id")
    def onchange_type_of_media_id(self):
        if self.type_of_media_id:
            return {'domain': {'target_media_id': [('media_type_id', '=', self.type_of_media_id.id)]}}
        else:
            return {'domain': {'target_media_id': [('media_type_id', '=', False)]}}

    @api.onchange("type_of_media_id")
    def onchange_diffusion_type_id(self):
        if self.type_of_media_id:
            return {'domain': {'diffusion_type_id': [('media_type', '=', self.type_of_media_id.id)]}}
        else:
            return {'domain': {'diffusion_type_id': [('media_type', '=', False)]}}

    @api.depends('expense_ids.amount')
    def _amount_total(self):
        for order in self:
            total = 0
            for line in order.expense_ids:
                total += line.amount
                order.amount_total = total

    @api.depends('expense_ids.amount_realized')
    def _get_total_spending(self):
        for order in self:
            total = 0
            for line in order.expense_ids:
                total += line.amount_realized
                order.total_spending = total

    def _get_url_direct_link(self):
        """
            génère l'url pour accéder directement au document en cours
        """
        res = {}
        res['view_type'] = 'form'
        res['model'] = 'survey.campaign'
        ir_menu_obj = self.env['ir.ui.menu']
        try:
            menu_ref_id = self.env['ir.model.data'].get_object_reference('base', 'edit_menu_access')
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            if menu_ref_id:
                menu = ir_menu_obj.search([('id', '=', menu_ref_id[1])])
                res['menu_id'] = menu.id
                res['action'] = menu.action.id
                res['id'] = self.id
            lien = werkzeug.url_encode(res)
            url = urljoin(base_url, "/web/?#%s" % (lien))
            self.url_link = url
            print(url)
        except:
            self.url_link = '#'

    url_link = fields.Char("Lien", compute=_get_url_direct_link)

    def _get_recipients_mails(self):
        group_id = \
            self.env['ir.model.data'].get_object_reference('sale_crm_extension', 'group_chef_service_commercial')[
                1]
        if group_id:
            group = self.env['res.groups'].browse(group_id)
            if group:
                if group.users:
                    email = ''
                    for user in group.users:
                        email += user.login + ';'
                    self.recipients_mails = email
                else:
                    self.recipients_mails = ''

    def send_notification(self, email_id, context=None):
        template_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', email_id)
        try:
            mail_templ = self.env['mail.template'].browse(template_id[1])
            result = mail_templ.send_mail(res_id=self.id, force_send=True)
            return True
        except:
            return False
