# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from urllib.parse import urljoin
import werkzeug


class ResPartnerUpdate(models.Model):
    _name = 'res.partner.update'

    ref = fields.Char('Référence')
    name = fields.Char('name')
    website = fields.Char('website')
    street = fields.Char('street')
    city = fields.Char('city')
    mobile = fields.Char('mobile')
    phone = fields.Char('phone')
    partner_phone = fields.Char('partner_phone')
    partner_mobile = fields.Char('partner_mobile')
    email = fields.Char('email')
    function = fields.Char('function')
    partner_name = fields.Char('partner_name')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_submit_to_dcm(self):
        """
        Submit to DCM
        :return:
        """
        for rec in self:
            self.chef_service_commercial_id = self.env.user.id
            result = self.send_notification('email_dcm_template_submit_create_customer')
            if result:
                rec.state = 'dcm'

    def action_submit_to_daf(self):
        """
        Submit to DAF
        :return:
        """
        for rec in self:
            self.dcm_id = self.env.user.id
            result = self.send_notification('email_dcm_template_submit_create_customer')
            if result:
                rec.state = 'daf'

    def action_daf(self):
        """
        Submit to account
        :return:
        """
        for rec in self:
            self.daf_id = self.env.user.id
            result = self.send_notification('email_dcm_template_submit_create_customer')
            if result:
                rec.state = 'account'

    def action_account(self):
        for rec in self:
            if rec.type_partner == 'pub':
                rec.ref = self.env['ir.sequence'].next_by_code('pub.partner') or '/'

            if rec.type_partner == 'imp':
                rec.ref = self.env['ir.sequence'].next_by_code('imp.partner') or '/'

            if rec.type_partner == 'dist':
                rec.ref = self.env['ir.sequence'].next_by_code('dist.partner') or '/'

            if rec.type_partner == 'avis':
                rec.ref = self.env['ir.sequence'].next_by_code('avis.partner') or '/'
            rec.state = 'done'

    def action_refuse(self):
        """
        Refuse or Rejected create customer
        :return:
        """
        for rec in self:
            if rec.state == 'dcm':
                rec.state = 'draft'
            if rec.state == 'daf':
                rec.state = 'dcm'
            if rec.state == 'account':
                rec.state = 'daf'

    refuse_raison = fields.Char('Raison du refus DCM', track_visibility='onchange')
    refuse_raison_daf = fields.Char('Raison du refus DAF', track_visibility='onchange')
    refuse_raison_account = fields.Char('Raison du refus Chef Comptable', track_visibility='onchange')
    state = fields.Selection([('draft', 'Chef Service Commercial'),
                              ('dcm', 'DCM'),
                              ('daf', 'DAF'),
                              ('account', 'Chef comptable'),
                              ('done', 'Terminé'), ], 'Etat', default='draft')
    chef_service_commercial_id = fields.Many2one("res.users", "Chef Service Commercial",
                                                 default=lambda self: self.env.user.id)
    dcm_id = fields.Many2one("res.users", "DCM")
    daf_id = fields.Many2one("res.users", "DAF")
    account_id = fields.Many2one("res.users", "Chef Comptable")
    current_user_id = fields.Many2one("res.users", "Utilisateur Courant")
    recipients_mails = fields.Char('Diffusion email', compute='_get_recipients_mails')
    is_spanco = fields.Boolean('SPANCO', default=False)

    capital = fields.Float('Capital')
    rccm = fields.Char(string='RCCM', help='Régistre du Commerce et du Crédit Mobilier')
    taxpayer_account = fields.Char('Compte Contribuable')
    tax_declaration = fields.Char('Déclaration Fiscale')
    cnps = fields.Char(string='N°CNPS', help='Caisse Nationale de Prévoyance Sociale')
    legal_form_id = fields.Many2one('forme.juridique', 'Forme juridique')

    group_id = fields.Many2one('res.partner.group', 'Groupe de société')
    branch_activity = fields.Char('Secteur d’activité', )
    branch_activity1 = fields.Many2one('res.partner.industry', 'Secteur d’activité', )
    primary_activity = fields.Many2one('principal.activity', 'Activité principale')
    company_siz_id = fields.Many2one('enterprise.size', 'Taille de la société')
    number_employees = fields.Integer('Nombre de salariés : ', compute='get_total_number_of_employees')
    number_man = fields.Integer('Nombre d’hommes')
    number_woman = fields.Integer('Nombre de Femmes')
    company_turnover = fields.Float('Chiffre d’affaire de la société')
    monetary = fields.Selection([('eur', 'EUR'),
                                 ('usd', 'USD'),
                                 ('xof', 'XOF')], default='xof')
    budget = fields.Float('Budget')

    partner_name = fields.Char(string='Nom du contact')
    partner_email = fields.Char(string='Email du contact')
    partner_phone = fields.Char(string='Téléphone du contact')
    partner_mobile = fields.Char(string='Mobile du contact')

    manager_name = fields.Char('Nom du dirigeant')
    manager_function = fields.Char('Fonction du dirigeant')

    tax_number = fields.Char('Numéro fiscale')
    fax = fields.Char('Fax')
    activity_ids = fields.One2many('mail.activity', 'customer_id', 'Visites dédiées au client')
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

    def _get_url_direct_link(self):
        """
            génère l'url pour accéder directement au document en cours
        """
        res = {}
        res['view_type'] = 'form'
        res['model'] = 'res.partner'
        ir_menu_obj = self.env['ir.ui.menu']
        try:
            menu_ref_id = self.env['ir.model.data'].get_object_reference('sale', 'res_partner_menu')
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

    def send_notification(self, email_id, context=None):
        template_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', email_id)
        try:
            mail_templ = self.env['mail.template'].browse(template_id[1])
            result = mail_templ.send_mail(res_id=self.id, force_send=True)
            return True
        except:
            return False

    def _get_recipients_mails(self):
        if self.state == 'draft':
            group_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', 'group_marketing_director')[
                1]
        if self.state == 'dcm':
            group_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', 'group_financial_director')[
                1]
        if self.state == 'daf':
            group_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', 'group_head_account')[1]
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

    @api.depends('number_man', 'number_woman')
    def get_total_number_of_employees(self):
        for rec in self:
            rec.number_employees = rec.number_man + rec.number_woman
            return rec.number_employees

    @api.depends('branch_activity1')
    def _compute_branch_activity(self):
        for partner in self:
            partner.industry_id = partner.branch_activity1.id if partner.branch_activity1 else False

    def _write_industry_id(self):
        for partner in self:
            partner.branch_activity1 = partner.industry_id.id if partner.industry_id else False
