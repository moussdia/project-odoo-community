# -*- coding:utf-8 -*-
from urllib.parse import urljoin

import werkzeug

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class RejectRaison(models.TransientModel):
    _name = 'create.lead'

    suspect_ids = fields.Many2many('survey.suspect', domain=[('attribute', '=', 'no'), ], string='Suspect')
    commercial_team_id = fields.Many2one('crm.team', string='Equipe commerciale')
    commercial_id = fields.Many2one('res.users', string='Commerciale')
    survey_campaign_id = fields.Integer('Campagne ID', store=True)
    survey_study_id = fields.Integer('Etude ID', store=True)
    marketing_name = fields.Char('Nom de la campagne', store=True)
    study_name = fields.Char('Nom de l\'étude', store=True)
    user_email = fields.Char('Email', compute='action_create_lead')

    @api.onchange("survey_study_id")
    def onchange_study_type(self):
        for rec in self:
            survey_study_id = self.env['survey.survey'].browse(rec.survey_study_id)
            rec.study_name = survey_study_id.title

    @api.onchange("survey_campaign_id")
    def onchange_marketing_type(self):
        for rec in self:
            survey_campaign_id = self.env['survey.campaign'].browse(rec.survey_campaign_id)
            rec.marketing_name = survey_campaign_id.name

    @api.onchange("commercial_team_id")
    def onchange_commercial_team_id(self):
        if self.commercial_team_id:
            return {'domain': {'commercial_id': [('sale_team_id', '=', self.commercial_team_id.id)]}}
        else:
            return {'domain': {'commercial_id': [('sale_team_id', '=', False)]}}

    def _get_url_direct_link(self):
        """
            génère l'url pour accéder directement au document en cours
        """
        res = {}
        res['view_type'] = 'form'
        res['model'] = 'res.partner'
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

    def _get_mail_destination(self):
        followers = self.user_email
        print('Mails followers:', followers)

    def send_mail(self, email_id, context=None):
        template_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', email_id)
        try:
            mail_templ = self.env['mail.template'].browse(template_id[1])
            result = mail_templ.send_mail(res_id=self.id, force_send=True)
            print('result % ', result)
            return True
        except Exception as e:
            print('>>>> errror', str(e))
            return False

    def action_create_lead(self):
        for rec in self:
            if rec.suspect_ids:
                rec.user_email = rec.commercial_id.login
                for guest in rec.suspect_ids:
                    goal_obj = {
                        'user_id': rec.commercial_id.id,
                        'name': guest.name + ' Opportunité',
                        'street': guest.address if guest.address else False,
                        'city': guest.city if guest.city else False,
                        'contact_name': guest.name if guest.name else False,
                        'partner_email': guest.email if guest.email else False,
                        'function': guest.function if guest.function else False,
                        'mobile': guest.contact if guest.contact else False,
                        'phone': guest.contact2 if guest.contact2 else False,
                        'type': 'opportunity',
                        'survey_campaign_id': rec.survey_campaign_id or '',
                        'survey_study_id': rec.survey_study_id or '',
                    }
                    res = self.env['crm.lead'].create(goal_obj)
                    suspect_id = self.env['survey.suspect'].search([('id', '=', guest.id)])
                    if suspect_id:
                        suspect_id.attribute = 'yes'
                    self._get_mail_destination()
                    self.send_mail('campaign_create_suspect_send_mail')
            else:
                raise ValidationError("Veuillez sélectionner un ou plusieur(s) suspect(s)!!!")
