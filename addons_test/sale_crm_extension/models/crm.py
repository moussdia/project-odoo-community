# -*- coding: utf-8 -*-
import base64
import string
import webbrowser

from odoo import fields, models, tools, api
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import osv
from odoo.tools.translate import _
from urllib.parse import urljoin
import werkzeug
from datetime import datetime
import requests


class Stage(models.Model):
    _inherit = 'crm.stage'

    step = fields.Selection([('suspect', 'Suspect'),
                             ('prospect', 'Prospect'),
                             ('analyse', 'Analyse'),
                             ('negociation', 'Négociation'),
                             ('closing', 'Closing'),
                             ('order_ongoing', 'Order')], 'Etape', required=True)

    probability = fields.Float(string="Probabilité", required=True)


class Team(models.Model):
    _inherit = 'crm.team'

    enterprise_size_ids = fields.Many2many('enterprise.size', column1='team_id', column2='size_id',
                                           string='Taille de la société')
    product_ids = fields.Many2many('product.template', column1='team_id', column2='product_id', string='Produit')
    geographic_zone = fields.Many2one('localization.zone', 'Zone géographique')
    activity_sector_ids = fields.Many2many('res.partner.industry', column1='team_id', column2='industry_id',
                                           string='Secteur d’activité')
    team_goal = fields.Text('Objectif de l’équipe')


class CrmLead2opportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    def action_crm_lead2opportunity_partner(self):
        """
        :param self:
        :return:
        """
        res = super(CrmLead2opportunityPartner, self).action_crm_lead2opportunity_partner()
        self._get_mail_destination()
        return res

    mail_destination = fields.Char('Adresse mails')


class Lead(models.Model):
    _inherit = 'crm.lead'

    step = fields.Selection([('suspect', 'Suspect'),
                             ('prospect', 'Prospect'),
                             ('analyse', 'Analyse'),
                             ('negociation', 'Négociation'),
                             ('standby', 'Standby'),
                             ('closing', 'Closing'),
                             ('order_ongoing', 'Order')], 'Etape', related="stage_id.step", store=True)
    probability_percent = fields.Float('Probabilité', compute='_get_probability_percent')
    mail_destination = fields.Char('Adresse mails', compute='_get_mail_destination')
    group_id = fields.Many2one('res.partner.group', 'Groupe de société')
    company_phone = fields.Char('Téléphone')
    branch_activity = fields.Char('Secteur d’activité')
    branch_activity1 = fields.Many2one('res.partner.industry', 'Secteur d’activité')
    primary_activity = fields.Many2one('principal.activity', 'Activité principale')
    company_turnover = fields.Float('Chiffre d’affaire de la société')
    monetary = fields.Selection([('eur', 'EUR'),
                                 ('usd', 'USD'),
                                 ('xof', 'XOF')], default='xof')
    manager_name = fields.Char('Nom du dirigeant')
    manager_function = fields.Char('Fonction du dirigeant')
    company_email = fields.Char('Adresse email')
    rccm = fields.Char(string='RCCM', help='Régistre du Commerce et du Crédit Mobilier')
    taxpayer_account = fields.Char('Compte Contribuable')
    tax_declaration = fields.Char('Déclaration Fiscale')
    cnps = fields.Char(string='N°CNPS', help='Caisse Nationale de Prévoyance Sociale')
    capital = fields.Float('Capital')
    bar = fields.Integer('Progressbar', default=10)
    number_employees = fields.Integer('Nombre de salariés : ', compute='get_total_number_of_employees')
    number_man = fields.Integer('Nombre d’hommes')
    number_woman = fields.Integer('Nombre de Femmes')
    deal = fields.Selection([('sure', 'Certain (100%)'),
                             ('unsure', 'Incertain (0%)'),
                             ('medium', 'Medium (50%)'), ], 'Deal')
    geolocalisation = fields.Many2one('localization.zone', 'Géolocalisation')
    company_siz_id = fields.Many2one('enterprise.size', 'Taille de la société')
    legal_form_id = fields.Many2one('forme.juridique', 'Forme juridique')
    origin_deal_id = fields.Many2one('deal.origin', 'Origine du deal')

    """fields carte identite"""
    job = fields.Many2one('crm.job', 'Métier')
    market = fields.Selection([('b2b', 'B2B'),
                               ('b2c', 'B2C')], 'Marché')
    organization = fields.Many2many('res.partner', string='Organisation')
    development_strategy = fields.Char('Stratégie de développement')

    """
    fields historique
    """
    order_history_ids = fields.One2many('sale.order.history', 'lead_id', string="Bon de commandes", copy=True,
                                        help="Bon decommandes engrangés")

    income_realized = fields.Monetary('C.A réalisé', currency_field='company_currency')
    margin = fields.Float('Marge brute commerciale', compute='get_total_expense')  #

    expense = fields.Float('Charges maillage', compute='get_expense_value')  #
    expense_exploitation = fields.Float('Charges exploitation')
    expense_total = fields.Float('Charges', compute='_get_total_expense')  #
    notice = fields.Selection([('satisfied', 'Satisfait'),
                               ('unsatisfied', 'Non Satisfait')], 'Avis')
    opportunity = fields.Char('Opportunité')
    threat = fields.Char('Menaces')
    strength = fields.Char('Force')
    weakness = fields.Char('Faiblesse')
    income = fields.Float('Chiffre d’affaire')

    attrait = fields.Text('Attrait', help='En quoi ce compte est-il intéressant stratégiquement sur le '
                                          'long terme pour notre société?')
    advantage = fields.Text(help='Pourquoi ce compte s’intéresse-t-il stratégiquement sur le long terme '
                                 'à notre société?')
    position = fields.Char('Positionnement')
    analyse_emoff = fields.Text('Analyse EMOFF',
                                help='Pourquoi ce compte s’intéresse-t-il stratégiquement sur le long terme à notre société ?')
    decision_organization = fields.Char('Organisation de décision')
    grid = fields.Text('GRID', help='Comment le compte s’organise-t-il pour acheter et décider ? '
                                    'le GRID (groupe réel d’influence et de décision) nous est-il '
                                    'favorable? quels sont les alliés? les opposants ?')
    grid_opinion = fields.Selection([('favorable', 'Favorabe'),
                                     ('defavorable', 'Défavorabe')], 'Avis GRID')

    managers_name = fields.Many2many('res.partner', 'managers_name_partner_rel', 'managers_name_id', 'partner_id',
                                     string='Nom des personnes dirigeantes')
    power_of_decision = fields.Many2one('hr.job', 'Pouvoir de décision')

    internal_team = fields.Many2many('res.partner', 'internal_team_partner_rel', 'internal_team_name_id',
                                     'partner_id', string='Equipe interne', domain=[('company_type', '=', 'person')])
    decision_making_body = fields.Many2many('res.partner', 'team_decision_making_body_partner_rel', 'lead_id',
                                            'partner_id', string='Organe de décision',
                                            domain=[('company_type', '=', 'person')])
    budget = fields.Float('Budget')
    reference = fields.Char("Référence", readonly=True)
    date_localization = fields.Date(string='Geolocation Date')
    lead_altitude = fields.Char('Alt')
    lead_latitude = fields.Char('Lat')
    lead_longitude = fields.Char('Long')
    is_customer = fields.Selection([('yes', 'Oui'),
                                    ('no', 'Non')], default='no', string='Client existant ?')
    lead_manager_ids = fields.One2many('crm.lead.manager', 'lead_id', 'Personnes dirigeante & pouvoir de décision')
    activity_ids = fields.One2many(comodel_name='mail.activity', inverse_name='res_id', string='Plan d\'action',
                                   ondelete='cascade')
    google_map_location = fields.Char(string='Google Map Location')
    partner_email = fields.Char(string='Email')
    partner_phone = fields.Char(string='Téléphone')
    is_spanco = fields.Boolean('SPANCO', default=True)
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Personne Physique'), ('company', 'Personne Morale')],
                                    compute='_compute_company_type', inverse='_write_company_type')
    is_company = fields.Boolean(string='Est une société', default=False,
                                help="Check if the contact is a company, otherwise it is a person")
    _sql_constraints = [('rccm_unique', 'unique(rccm)', 'Le registre de commerce existe déjà.')
        , ('taxpayer_account_unique', 'unique(taxpayer_account)', 'le compte contribuable existe déjà')]
    sponsor = fields.Many2one('res.partner', 'Parrain')
    expense_ids = fields.One2many('sale.order.exploitation', 'crm_id', string="Charges d'exploitation",
                                  help="Toutes les charges lié à k’affaire")
    expense_total_exploitation = fields.Float('Charges exploitation', compute='_expense_total', store=True)
    is_standby = fields.Boolean('Est stand-by', default=False)
    probability = fields.Float('Probability', copy=False)
    probability_of_being_chosen = fields.Float('Probabilité d’être choisi', copy=False,
                                               help="Probabilité d’être choisi, le stade de k’affaire")
    automated_probability = fields.Float('Automated Probability', readonly=True, )
    is_automated_probability = fields.Boolean('Is automated probability?', default=False)
    activity_history_ids = fields.One2many('mail.activity.history', 'lead_id', string='historique')
    work_advancement = fields.Float('Avancement des traveaux')
    percentage = fields.Char('Pourcentage', default='%')
    year_id = fields.Many2one('sale.year', 'Exercice commercial', domain=[('state', '=', 'open')])
    period_id = fields.Many2one('sale.periodicity', 'Periode commerciale')
    account_history = fields.Text('Historique du compte',
                                  help="Date de naissance de k’entreprise, d’où elle vient et ou elle va")
    estimated_order_date = fields.Date('Date prévisionnelle de commande')
    amount_untaxed = fields.Float('Montant du Deal')
    standby_raison = fields.Text('Motif du réjet', track_visibility='onchange')
    customer_category = fields.Selection([('gros', 'Gros clients'),
                                          ('moyen', 'Clients moyens'),
                                          ('petit', 'Petit clients')], 'Catégorie client')
    potential_customer = fields.Selection([('gros', 'Gros potentiel'),
                                           ('moyen', 'Moyens potentiel'),
                                           ('petit', 'Petit potentiel')], 'Potentiel client')
    type_partner = fields.Selection([('pub', 'Régie publicitaire'),
                                     ('imp', 'Imprimerie'),
                                     ('dist', 'Réseau Distribution'),
                                     ('avis', 'Avis & communiqués')], string='Typed de client')
    litigation = fields.Selection([('yes', 'Oui'),
                                   ('no', 'Non')], default='no', string="Litige ?")
    reason_for_the_dispute = fields.Text('motif du litige')
    survey_campaign_id = fields.Many2one('survey.campaign', string='Campagne')
    survey_study_id = fields.Many2one('survey.survey', string='Etude')
    customer_team_ids = fields.One2many('crm.lead.customer.team', 'lead_id', string='Equipe chez le client')
    allies_ids = fields.One2many('crm.lead.allies', 'lead_id', string='Allié')
    opponent_ids = fields.One2many('crm.lead.opponent', 'lead_id', string='Opposant')

    @api.depends('step')
    def _get_probability_percent(self):
        for rec in self:
            if rec.step == 'suspect':
                rec.probability_percent = 0.00
            if rec.step == 'prospect':
                rec.probability_percent = 10.00
            if rec.step == 'analyse':
                rec.probability_percent = 50.00
            if rec.step == 'negociation':
                rec.probability_percent = 70.00
            if rec.step == 'closing':
                rec.probability_percent = 90.00
            if rec.step == 'order_ongoing':
                rec.probability_percent = 100.00

    def print_consolidated_tour_plan_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('sale_crm_extension.action_consolidated_tour_plan').report_action(self, data=data)

    def action_new_quotation(self):
        action = self.env.ref("sale_crm.sale_action_quotations_new").read()[0]
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_team_id': self.team_id.id,
            'default_year_id': self.year_id.id,
            'default_period_id': self.period_id.id,
            'default_lead_id': self.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
        }
        return action

    @api.onchange('name')
    def get_opportunity_order(self):
        for oppor in self:
            if oppor.id:
                oppor.name = oppor.quotation_count.name

    @api.depends('expense_ids')
    def _expense_total(self):
        for order in self:
            expense_total_exploitation = 0
            for expense in order.expense_ids:
                expense_total_exploitation += expense.amount
            order.expense_total_exploitation = expense_total_exploitation

    @api.depends('expense_total_exploitation', 'expense')
    def get_total_expense(self):
        for rec in self:
            total_expense = rec.expense + rec.expense_total_exploitation
            print('TOTAL', total_expense)
            rec.margin = rec.sale_amount_total - total_expense
            print('Marge', self.margin)

    def action_restore(self):
        self.is_standby = False

    @api.depends('lead_manager_ids')
    def get_expense_value(self):
        """
        Get expence values
        """
        expense = 0
        for rec in self:
            if rec.lead_manager_ids or len(rec.lead_manager_ids) != 0:
                for manager_id in rec.lead_manager_ids:
                    expense += manager_id.business_lunch_budget if manager_id.business_lunch_budget else 0
            rec.expense = expense

    @api.depends('expense', 'expense_exploitation')
    def _get_total_expense(self):
        for rec in self:
            rec.expense_total = rec.expense if rec.expense else 0 + rec.expense_exploitation if rec.expense_exploitation else 0

    def send_mail(self, email_id):
        """
        Send mail
        :param email_id:
        :return:
        """
        template_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', email_id)
        try:
            mail_templ = self.env['mail.template'].browse(template_id[1])
            result = mail_templ.send_mail(res_id=self.id, force_send=True)
            print('result % ', result)
            return True
        except Exception as e:
            print('>>>> error', str(e))
            return False

    def _get_mail_destination(self):
        """
        Send email
        :param self:
        :return:
        """
        followers = ''
        ir_model_data = self.env['ir.model.data']
        group_obj = self.env['res.groups']
        model_id = ir_model_data.get_object_reference('sale_crm_extension', 'group_head_marketing')[1]
        group_id = group_obj.browse(model_id)
        for user in group_id.users:
            followers = '%s;%s' % (user.login, followers)
        self.mail_destination = followers

    @api.depends('number_man', 'number_woman')
    def get_total_number_of_employees(self):
        for rec in self:
            rec.number_employees = rec.number_man + rec.number_woman
            return rec.number_employees

    @api.model
    def create(self, vals):
        crm_stage = self.env['crm.stage'].browse(vals.get('stage_id'))
        if crm_stage and crm_stage.step != 'suspect':
            raise ValidationError(
                "Vous ne pouvez pas créer de suspect à cette étape du processus de vente")
        res = super(Lead, self).create(vals)
        return res

    def write(self, vals):

        """
        Avoid step jumps from one step to another at the level
        Create lead as customer
        :param vals:
        :return:
        """
        previous_stage = self.stage_id
        res = super(Lead, self).write(vals)
        next_stage = self.stage_id
        crm_stage = self.env['crm.stage'].browse(self.stage_id.id)

        # if crm_stage.step in ['analyse']:
        #     if self.capital == 0.00 or self.legal_form_id == False or self.rccm == False or self.branch_activity1 == False \
        #             or self.primary_activity == False or self.company_siz_id == False \
        #             or self.customer_category == False or self.potential_customer == False:
        #         raise ValidationError("Tous les champs obligatoires doivent être renseignés")

        if next_stage and previous_stage:
            if next_stage.sequence > previous_stage.sequence + 1:
                raise ValidationError(
                    "Vous ne pouvez pas sauter plus d'une étape")

            if previous_stage.sequence > next_stage.sequence + 1:
                raise ValidationError(
                    "Vous ne pouvez pas sauter plus d'une étape")

        if crm_stage.step == 'order_ongoing':
            exis_data_id = self.env['res.partner'].search([('name', '=', self.partner_name)])
            if exis_data_id:
                #     raise osv.except_osv(_('Action Invalide !'), _('Le nom existe déjà.'))
                exis_data_id.write({
                    'company_type': 'company',
                    'type': 'contact',
                    'name': self.partner_name,
                    'street': self.street,
                    'street2': self.street2,
                    'city': self.city,
                    'state_id': self.state_id.id if self.state_id else False,
                    'zip': self.zip,
                    'country_id': self.country_id.id if self.country_id else False,
                    'title': self.title.id if self.title else False,
                    'function': self.function,
                    'phone': self.phone,
                    'mobile': self.mobile,
                    'is_spanco': self.is_spanco,
                    'company_type': self.company_type,
                    'capital': self.capital,
                    'rccm': self.rccm,
                    'taxpayer_account': self.taxpayer_account,
                    'tax_declaration': self.tax_declaration,
                    'cnps': self.cnps,
                    'group_id': self.group_id.id if self.group_id else False,
                    'branch_activity1': self.branch_activity1.id if self.branch_activity1 else False,
                    'primary_activity': self.primary_activity.id if self.primary_activity else False,
                    'company_siz_id': self.company_siz_id.id if self.company_siz_id else False,
                    'legal_form_id': self.legal_form_id.id if self.legal_form_id else False,
                    'number_employees': self.number_employees,
                    'number_man': self.number_man,
                    'number_woman': self.number_woman,
                    'company_turnover': self.company_turnover,
                    'budget': self.budget,
                    'industry_id': self.branch_activity1.id if self.branch_activity1 else False,
                    'partner_name': self.contact_name,
                    'partner_email': self.partner_email,
                    'partner_phone': self.partner_phone,
                    'partner_mobile': self.mobile,
                    'manager_name': self.manager_name,
                    'manager_function': self.manager_function,
                    'email': self.email_from,
                    'website': self.website,
                    'partner_latitude': self.lead_latitude,
                    'partner_longitude': self.lead_longitude,
                    'customer_category': self.customer_category,
                    'potential_customer': self.potential_customer,
                    'type_partner': self.type_partner,
                })

            if not exis_data_id:
                partner_obj = self.env['res.partner']
                reference = self.env['ir.sequence'].next_by_code('res.partner') or '/'
                partner_obj.create({
                    'company_type': 'company',
                    'type': 'contact',
                    'name': self.partner_name,
                    'street': self.street,
                    'street2': self.street2,
                    'city': self.city,
                    'state_id': self.state_id.id if self.state_id else False,
                    'zip': self.zip,
                    'country_id': self.country_id.id if self.country_id else False,
                    'title': self.title.id if self.title else False,
                    'function': self.function,
                    'phone': self.phone,
                    'mobile': self.mobile,
                    'is_spanco': self.is_spanco,
                    'company_type': self.company_type,
                    'capital': self.capital,
                    'rccm': self.rccm,
                    'taxpayer_account': self.taxpayer_account,
                    'tax_declaration': self.tax_declaration,
                    'cnps': self.cnps,
                    'group_id': self.group_id.id if self.group_id else False,
                    'branch_activity1': self.branch_activity1.id if self.branch_activity1 else False,
                    'primary_activity': self.primary_activity.id if self.primary_activity else False,
                    'company_siz_id': self.company_siz_id.id if self.company_siz_id else False,
                    'legal_form_id': self.legal_form_id.id if self.legal_form_id else False,
                    'number_employees': self.number_employees,
                    'number_man': self.number_man,
                    'number_woman': self.number_woman,
                    'company_turnover': self.company_turnover,
                    'budget': self.budget,
                    'industry_id': self.branch_activity1.id if self.branch_activity1 else False,
                    'partner_name': self.contact_name,
                    'partner_email': self.partner_email,
                    'partner_phone': self.partner_phone,
                    'partner_mobile': self.mobile,
                    'manager_name': self.manager_name,
                    'manager_function': self.manager_function,
                    'email': self.email_from,
                    'website': self.website,
                    'partner_latitude': self.lead_latitude,
                    'partner_longitude': self.lead_longitude,
                    'type_partner': self.type_partner,
                })
                print('partner customer created', partner_obj)
        return res

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.step == 'suspect':
            self.step = self.stage_id.step
        if self.stage_id:
            crm_stage = self.env['crm.stage'].browse(self.stage_id.id)
            if crm_stage:
                self.probability = crm_stage.probability
                self.automated_probability = crm_stage.probability

    def _compute_probability(self):
        if self.stage_id:
            crm_stage = self.env['crm.stage'].browse(self.stage_id.id)
            if crm_stage:
                self.probability = crm_stage.probability
                self.automated_probability = crm_stage.probability

    def _compute_automated_probability(self):
        if self.stage_id:
            crm_stage = self.env['crm.stage'].browse(self.stage_id.id)
            if crm_stage:
                self.automated_probability = crm_stage.probability

    @api.model
    def _geo_localize(self, street='', zip='', city='', state='', country=''):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    def geo_localize(self):
        # We need country names in English below
        geo_obj = self.env['base.geocoder']
        for lead in self.with_context(lang='fr_FR'):
            result = self._geo_localize(lead.street,
                                        lead.zip,
                                        lead.city,
                                        lead.state_id.name,
                                        lead.country_id.name)

            if result:
                print('result geolocalization', result)
                lead.write({
                    'lead_latitude': result[0],
                    'lead_longitude': result[1],
                    'date_localization': fields.Date.context_today(lead),
                    # 'lead_altitude': self.get_elevation(result[0], result[1]),
                })
        return True

    @api.onchange('is_customer')
    def onchange_is_customer(self):
        """
        Reset sale.order.history if customer doesn't exist
        :return:
        """
        for lead in self:
            if lead.is_customer:
                if lead.is_customer == 'no':
                    lead.order_history_ids = None
                    lead.partner_id = None
                    lead.partner_name = None
                    lead.street = None
                    lead.street2 = None
                    lead.city = None
                    lead.zip = None
                    lead.country_id = None
                    lead.website = None
                    lead.lang_id = None
                    lead.year_id = None
                    lead.period_id = None
                    lead.email_from = None
                    lead.phone = None
                    lead.contact_name = None
                    lead.function = None
                    lead.partner_phone = None
                    lead.mobile = None
                    lead.manager_name = None
                    lead.manager_function = None
                    lead.priority = None
                    lead.source_id = None
                    lead.type_partner = None

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Load order event change partner
        :return:
        """
        for lead in self:
            if lead.partner_id:
                history = self.env['sale.order.history']
                order_ids = self.env['sale.order'].search(
                    [('partner_id', '=', lead.partner_id.id), ('state', '=', 'sale')])
                print('devis %s ' % order_ids)
                amount_total = 0
                expense_total = 0
                lead.order_history_ids = None
                if order_ids:
                    for order in order_ids:
                        lead.order_history_ids += history.create({
                            'name': order.name,
                            'amount_untaxed': order.amount_untaxed,
                            'evaluation_id': order.evaluation_id.id if order.evaluation_id else False,
                            'lead_id': lead.id,
                        })
                        amount_total += order.amount_untaxed
                        if len(order.expense_ids) > 0:
                            for expense in order.expense_ids:
                                expense_total += expense.amount

                print("amount_total", amount_total)
                print("expense_total", expense_total)

                # lead.income_realised = amount_total
                # lead.margin = lead.income_realised - expense_total

                if lead.partner_id.child_ids.filtered(lambda r: r.type == "contact"):
                    for child in lead.partner_id.child_ids.filtered(lambda r: r.type == "contact"):
                        lead.contact_name = child.name
                        lead.title = child.title.id if child.title else False
                        lead.function = child.function
                        lead.mobile = child.mobile

    def _compute_order_ids(self):
        """
        Load sale.order.history after save record
        :return:
        """
        history = self.env['sale.order.history']
        for lead in self:
            if lead.partner_id:
                order_ids = self.env['sale.order'].search(
                    [('partner_id', '=', lead.partner_id.id), ('state', '=', 'sale')])
                print('bon de commandes %s ' % order_ids)
                lead.order_history_ids = None
                if order_ids:
                    for rec in order_ids:
                        lead.order_history_ids += history.create({
                            'name': rec.name,
                            'amount_untaxed': rec.amount_untaxed,
                            'evaluation_id': rec.evaluation_id.id if rec.evaluation_id else False,
                            'lead_id': rec.id,
                        })

    def open_google_maps(self):
        for lead in self.with_context(lang='fr_FR'):
            if lead.geo_localize():
                # gmap = 'https://www.google.com/maps/?q=' + str(lead.lead_latitude) + ',' + str(lead.lead_longitude)
                #              return {
                #     'type': 'ir.actions.act_url',
                #     'url': gmap,
                #     'target': '_blank',
                # }
                return True

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = 'company' if partner.is_company else 'person'

    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'

    @api.constrains('rccm')
    def _check_rccm(self):
        for lead in self:
            if lead.rccm:
                lead_id = self.env['crm.lead'].search([('rccm', '=', lead.rccm)])
                if lead_id:
                    print('NOK')

    @api.constrains('taxpayer_account')
    def _check_taxpayer_account(self):
        for lead in self:
            if lead.taxpayer_account:
                lead_id = self.env['crm.lead'].search([('taxpayer_account', '=', lead.taxpayer_account)])
                if lead_id:
                    print('NOK')

    """ code for creating new client inherited from crm
    """

    def _create_lead_partner(self):
        """ Create a partner from lead data
            :returns res.partner record
        """
        Partner = self.env['res.partner']
        contact_name = self.contact_name
        if not contact_name:
            contact_name = Partner._parse_partner_name(self.email_from)[0] if self.email_from else False

        if self.partner_name:
            partner_company = Partner.create(self._create_lead_partner_data(self.partner_name, True))
        elif self.partner_id:
            partner_company = self.partner_id
        else:
            partner_company = None

        # if contact_name:
        #     return Partner.create(self._create_lead_partner_data(contact_name, False, partner_company.id if partner_company else False))

        if partner_company:
            return partner_company
        return Partner.create(self._create_lead_partner_data(self.name, False))

    """ inheritance function
    """

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order',
                 'order_ids.company_id')
    def _compute_sale_data(self):
        for lead in self:
            total = 0.0
            quotation_cnt = 0
            sale_order_cnt = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.order_ids:
                if order.state in (
                        'draft', 'sent', 'submitted', 'validated', 'discount_validated', 'discount_dcm_validated',
                        'discount_chef_service_com_validated', 'discount_dga_validated'):
                    quotation_cnt += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    sale_order_cnt += 1
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id,
                        order.date_order or fields.Date.today())
            lead.sale_amount_total = total
            lead.quotation_count = quotation_cnt
            lead.sale_order_count = sale_order_cnt


class CrmPromotion(models.Model):
    _name = 'crm.promotion'
    _rec_name = 'promotion'

    promotion = fields.Char('Promotion')
    technical_promotion = fields.Char('Technique promotionnelle')

    product = fields.Many2one('product.product', 'Produit')
    start_date = fields.Date('Date début')
    end_date = fields.Date('Date fin')
    steps = fields.Char('Démarche')
    risk_of_cannibalization = fields.Char('Risque de canibalisation')
    goal = fields.Char('Objectifs à atteindre')
    result_indicator = fields.Char('Indicateurs de résultat')
    reglementation = fields.Char('Indicateurs de résultat')
    planning = fields.Char('Planning')
    logistique = fields.Char('Logistique')
    available_stock = fields.Char('Stock disponible')
    budget = fields.Char('Budget')
    Seasonality = fields.Char('Saisonnalité')
    relay_to_inform = fields.Char('Relais pour informer')
    expected_delay_at_the_point_sale = fields.Char('Relais prévu sur le point de vente')
    media_relay_for_traffic_creation = fields.Char('Relais média pour création de trafic')
    direct_communication_delay = fields.Char('Relais communication directe')
    attractivity_degree = fields.Float('Degré d\'attractivité')
    originality_degree = fields.Float('Degré d\'originalité')
    competition_comparison = fields.Float('Comparaison concurrence')

    promotion_line_ids = fields.One2many('crm.promotion.line', 'prmotion_id', string='SUIVI')


class CrmPromotionLine(models.Model):
    _name = 'crm.promotion.line'

    prmotion_id = fields.Many2one('crm.promotion', 'Prmotion')
    result_indicator = fields.Selection([('quantitatifs', 'Quantitatifs'),
                                         ('qualitatifs', 'Qualitatifs')], default='quantitatifs')
    forecast = fields.Float('Prévisionnels')
    executed = fields.Float('Rélisés')
    difference = fields.Float('Ecarts')


class CrmKpi(models.Model):
    _name = 'crm.kpi'

    def print_productivity_and_performance_report(self):
        user_id = self.env.uid
        self._cr.execute('''
                            SELECT
                                COUNT(*) AS number_of_customer_visits
                            FROM
                                public.mail_activity
                            WHERE activity_type_id = 3 and user_id = %s
                       ''' % user_id)
        res = self._cr.fetchone()
        number_of_customer_visits = res[0]

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS number_of_cases
                            FROM
                                public.crm_lead
                            WHERE user_id = %s
                       ''' % user_id)
        res = self._cr.fetchone()
        number_of_cases = res[0]

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS big_customer
                            FROM
                                public.crm_lead
                            WHERE customer_category = 'gros' and user_id = %s
                       ''' % user_id)
        customer = self._cr.fetchone()
        big_customer = customer[0]

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS medium_customer
                            FROM
                                public.crm_lead
                            WHERE customer_category = 'moyen' and user_id = %s
                       ''' % user_id)
        customer1 = self._cr.fetchone()
        medium_customer = customer1[0]

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS small_customer
                            FROM
                                public.crm_lead
                            WHERE customer_category = 'petit' and user_id = %s
                       ''' % user_id)
        customer2 = self._cr.fetchone()
        small_customer = customer2[0]

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS new_client
                            FROM
                                public.crm_lead
                            WHERE step = 'suspect' and user_id = %s
                       ''' % user_id)
        new_client = self._cr.fetchone()
        new_client = new_client[0]

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS prospects
                            FROM
                                public.crm_lead
                            WHERE step = 'prospect' and user_id = %s
                       ''' % user_id)
        prospect_client = self._cr.fetchone()
        prospect_client = prospect_client[0]

        self._cr.execute('''
                            SELECT
                                SUM(company_turnover) AS turnover
                            FROM
                                public.crm_lead
                            WHERE step = 'prospect' and user_id = %s
                       ''' % user_id)
        client_turnover = self._cr.fetchone()
        client_turnover = client_turnover[0]

        self._cr.execute('''
                            SELECT
                                SUM(amount_untaxed) AS amount_untaxed
                            FROM
                                public.sale_order
                            WHERE state = 'sale' and user_id = %s
                       ''' % user_id)
        average_amount_of_business = self._cr.fetchone()
        average_amount_of_business = average_amount_of_business[0]

        if number_of_cases != 0 and average_amount_of_business != 0 and average_amount_of_business != None:
            average_amount = average_amount_of_business / number_of_cases
        else:
            average_amount = 0.0

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS partner
                            FROM
                                public.res_partner
                            WHERE state = 'done'
                       ''')
        active_partner = self._cr.fetchone()
        active_partner = active_partner[0]

        self._cr.execute('''
                            SELECT
                                COUNT(*) AS prospects
                            FROM
                                public.crm_lead
                            WHERE step = 'order_ongoing' and user_id = %s
                       ''' % user_id)
        lead_order_ongoing = self._cr.fetchone()
        lead_order_ongoing = lead_order_ongoing[0]

        if lead_order_ongoing != 0 and average_amount_of_business != 0:
            percentage = (lead_order_ongoing * 100) / number_of_cases
        else:
            percentage = 0.0

        activity_id = self.env['mail.activity'].search([('user_id', '=', self._uid)])
        print('activity_id', activity_id)

        big_customer_cursor = self.env.cr
        big_customer_cursor.execute("""
                                        SELECT
                                            COUNT(*)
                                        FROM
                                            crm_lead
                                        WHERE
                                            user_id = %s
                                        AND
                                           customer_category = 'gros'
                                        """ % user_id)

        big_customer_docs = big_customer_cursor.fetchone()[0]

        middle_customer_cursor = self.env.cr
        middle_customer_cursor.execute("""
                                          SELECT
                                              COUNT(*)
                                          FROM
                                              crm_lead
                                          WHERE
                                              user_id = %s
                                          AND
                                             customer_category = 'moyen'
                                          """ % user_id)

        middle_customer_docs = middle_customer_cursor.fetchone()[0]

        small_customer_cursor = self.env.cr
        small_customer_cursor.execute("""
                                         SELECT
                                             COUNT(*)
                                         FROM
                                             crm_lead
                                         WHERE
                                             user_id = %s
                                         AND
                                            customer_category = 'petit'
                                         """ % user_id)

        small_customer_docs = small_customer_cursor.fetchone()[0]

        number_of_prospecting_visits_cursor = self.env.cr
        number_of_prospecting_visits_cursor.execute("""
                                                        SELECT
                                                            COUNT(*)
                                                        FROM
                                                            crm_lead
                                                        WHERE
                                                            user_id = %s
                                                        AND
                                                            step = 'prospect'
                                                        """ % user_id)

        number_of_prospecting_visits_docs = number_of_prospecting_visits_cursor.fetchone()[0]

        amount_of_unpaid_bills_cursor = self.env.cr
        amount_of_unpaid_bills_cursor.execute("""
                                                 SELECT
                                                     SUM(amount_total_signed)
                                                 FROM
                                                     account_move
                                                 WHERE
                                                     invoice_user_id = %s
                                                 AND
                                                     payment_state = 'paid'
                                                """ % user_id)

        amount_of_unpaid_bills_docs = amount_of_unpaid_bills_cursor.fetchone()[0]

        number_of_disputes_cursor = self.env.cr
        number_of_disputes_cursor.execute("""
                                                    SELECT
                                                        COUNT(*)
                                                    FROM
                                                        crm_lead
                                                    WHERE
                                                        user_id = %s
                                                    AND
                                                        litigation = 'yes'
                                                """ % user_id)

        number_of_disputes_docs = number_of_disputes_cursor.fetchone()[0]

        vals = []

        obj = {
            'number_of_customer_visits': number_of_customer_visits,
            'number_of_cases': number_of_cases,
            'big_customer': big_customer,
            'medium_customer': medium_customer,
            'small_customer': small_customer,
            'number_of_new_clients': new_client,
            'number_of_prospects': prospect_client,
            'ca_of_new_clients': client_turnover,
            'average_amount_of_business': average_amount,
            'number_of_active_clients': active_partner,
            'rate_of_transformation_of_project_into_business': percentage,
            'small_customer_docs': small_customer_docs,
            'big_customer_docs': big_customer_docs,
            'middle_customer_docs': middle_customer_docs,
            'number_of_prospecting_visits': number_of_prospecting_visits_docs,
            'amount_of_unpaid_bills': amount_of_unpaid_bills_docs,
            'number_of_disputes': number_of_disputes_docs,

        }
        vals.append(obj)

        self.env['productivite.performance.view'].search([]).unlink()
        self.env['productivite.performance.view'].create(vals)

        data = {
            'ids': self.ids,
            'model': self._name,
        }
        return self.env.ref('sale_crm_extension.action_productivite_performance').report_action(self, data=data)


class ReportProductivityPerformenceReport(models.AbstractModel):
    _name = 'report.sale_crm_extension.report_productivite_performance'

    @api.model
    def _get_report_values(self, docids, data=None):
        productivite_performance_ids = self.env['productivite.performance.view'].search([])

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': productivite_performance_ids,
        }


class ReportConsolidatedTourPlan(models.AbstractModel):
    _name = 'report.sale_crm_extension.report_consolidated_tour_plan'

    @api.model
    def _get_report_values(self, docids, data=None):
        export_tour_plans_per_month = []
        export_annual_tour_plans = []
        export_customers = []

        total_customers = 0
        total_annual_tour_plans = 0
        total_tour_plans_per_month = 0

        cursor_customer_category_potential = self.env.cr
        cursor_customer_category_potential.execute("""
                                SELECT
                                    lead.customer_category,
                                    lead.potential_customer,
                                    COUNT(mail_activity_history.id) as count_activities
                                FROM
                                    mail_activity_history
                                INNER JOIN crm_lead AS lead
                                ON lead.id = mail_activity_history.lead_id
                                WHERE extract(month from mail_activity_history.date_deadline) = %s
                                GROUP BY
                                    lead.customer_category,
                                    lead.potential_customer
                                """ % (datetime.now().month))

        for export in cursor_customer_category_potential.fetchall():
            total_tour_plans_per_month = total_tour_plans_per_month + int(export[2])
            export_tour_plans_per_month.append(export)

        cursor_annual_tour_plans = self.env.cr
        cursor_annual_tour_plans.execute("""
                                SELECT
                                    lead.customer_category,
                                    lead.potential_customer,
                                    COUNT(mail_activity_history.id)
                                FROM
                                    mail_activity_history
                                INNER JOIN crm_lead AS lead
                                ON lead.id = mail_activity_history.lead_id
                                WHERE extract(year from mail_activity_history.date_deadline) = %s
                                GROUP BY
                                    lead.customer_category,
                                    lead.potential_customer
                                """ % (datetime.now().year))

        for export in cursor_annual_tour_plans.fetchall():
            total_annual_tour_plans = total_annual_tour_plans + int(export[2])
            export_annual_tour_plans.append(export)

        cursor_customer = self.env.cr
        cursor_customer.execute("""
                                SELECT
                                    crm_lead.customer_category,
                                    crm_lead.potential_customer,
                                    COUNT(partner.id)
                                FROM
                                    crm_lead
                                INNER JOIN res_partner AS partner
                                ON partner.id = crm_lead.partner_id
                                GROUP BY
                                    crm_lead.customer_category,
                                    crm_lead.potential_customer
                                """)

        for export in cursor_customer.fetchall():
            total_customers = total_customers + int(export[2])
            export_customers.append(export)

        return {
            'records': export_tour_plans_per_month,
            'annual_records': export_annual_tour_plans,
            'customers': export_customers,
            'total_customers': total_customers,
            'total_annual_tour_plans': total_annual_tour_plans,
            'total_tour_plans_per_month': total_tour_plans_per_month,
        }
