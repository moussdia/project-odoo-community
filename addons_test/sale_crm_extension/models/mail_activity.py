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


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    days = fields.Selection([('mon', 'Lundi'),
                             ('tue', 'Mardi'),
                             ('wed', 'Mercredi'),
                             ('thu', 'Jeudi'),
                             ('fri', 'Vendredi')], 'Jours')

    hours = fields.Selection([('1', '8h00-9h30'),
                              ('2', '10h00-11h30'),
                              ('3', '14h30-16h00'),
                              ('4', '16h30-17h30')], 'Hours')

    stat = fields.Selection([('accepted', 'Valable'),
                            ('refused', 'Annulé')], default='accepted', string='Etat')

    date_from = fields.Date('Date du')
    date_to = fields.Date('Au')
    date = fields.Date('Date', default=datetime.today().strftime('%Y-%m-%d'))
    todays_date = fields.Date('Date', default=datetime.today().strftime('%Y-%m-%d'))
    lead_id = fields.Many2one('crm.lead', 'Lead')
    lead_state = fields.Selection([('suspect', 'Suspect'),
                                   ('prospect', 'Prospect'),
                                   ('analyse', 'Analyse'),
                                   ('negociation', 'Négociation'),
                                   ('closing', 'Closing'),
                                   ('order_ongoing', 'Order')], 'Etape', related='lead_id.step', store=True)

    city = fields.Char('Villle')
    partner_name = fields.Char('Client')
    customer_id = fields.Many2one('res.partner', 'Client visité')

    modify_raison = fields.Char('Raison de la modification')
    cancel_raison = fields.Char('Raison d\'annulation')
    name = fields.Char(string="Numéro activité", readonly=True, required=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mail.activity.code') or 'New'

        result = super(MailActivity, self).create(vals)

        crm_lead = self.env['crm.lead'].search([('id', '=', result.res_id)])

        result['city'] = crm_lead.partner_id.city
        result['partner_name'] = crm_lead.partner_id.name

        self.env['mail.activity.history'].create({
            'activity_type_id': result.activity_type_id.id if result.activity_type_id else False,
            'summary': result.summary,
            'note': result.note,
            'date_deadline': result.date_deadline,
            'user_id': result.user_id.id if result.user_id else False,
            'state': result.state,
            'lead_id': result.res_id,
        })

        result.send_mail('sale_crm_extension_send_mail_template')
        return result

    def write(self, values):
        rec = super(MailActivity, self).write(values)
        if self.modify_raison:
            self.send_mail('sale_crm_extension_custom_mail_activity_template')

        return rec

    def _get_url_direct_link(self):
        """
            génère k'url pour accéder directement au document en cours
        """
        res = {}
        res['view_type'] = 'form'
        res['model'] = 'crm.lead'
        ir_menu_obj = self.env['ir.ui.menu']
        try:
            menu_ref_id = self.env['ir.model.data'].get_object_reference('crm', 'crm_lead_menu_my_activities')
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

    def _get_mail_destination(self):
        followers = ''
        ir_model_data = self.env['ir.model.data']
        group_obj = self.env['res.groups']
        model_id = ir_model_data.get_object_reference('sale_crm_extension', 'group_chef_service_commercial')[1]
        group_id = group_obj.browse(model_id)
        for user in group_id.users:
            followers = '%s;%s' % (user.login, followers)

        model_id = ir_model_data.get_object_reference('sale_crm_extension', 'group_marketing_director')[1]
        group_id = group_obj.browse(model_id)
        for user in group_id.users:
            followers = '%s;%s' % (user.login, followers)

        model_id = ir_model_data.get_object_reference('sale_crm_extension', 'group_sub_director')[1]
        group_id = group_obj.browse(model_id)
        for user in group_id.users:
            followers = '%s;%s' % (user.login, followers)

        self.mail_destination = followers
        print('Mails:', followers)

    def _get_followers_plan_tour(self):
        followers = ''
        ir_model_data = self.env['ir.model.data']
        group_obj = self.env['res.groups']
        group_users = []

        model_id = ir_model_data.get_object_reference(
            'sale_crm_extension',
            'group_director')[1]
        group_id = group_obj.browse(model_id)
        group_users.append(group_id.users)

        model_id = ir_model_data.get_object_reference(
            'sale_crm_extension',
            'group_chef_service_commercial')[1]
        group_id = group_obj.browse(model_id)
        group_users.append(group_id.users)

        model_id = ir_model_data.get_object_reference(
            'sale_crm_extension',
            'group_sub_director')[1]
        group_id = group_obj.browse(model_id)
        group_users.append(group_id.users)

        model_id = ir_model_data.get_object_reference(
            'sale_crm_extension',
            'module_access_sale_crm')[1]
        group_id = group_obj.browse(model_id)
        group_users.append(group_id.users)

        model_id = ir_model_data.get_object_reference(
            'sale_crm_extension',
            'group_chef_service_commercial')[1]
        group_id = group_obj.browse(model_id)
        group_users.append(group_id.users)

        model_id = ir_model_data.get_object_reference(
            'sale_crm_extension',
            'group_chef_service_administration_vente')[1]
        group_id = group_obj.browse(model_id)
        group_users.append(group_id.users)

        model_id = ir_model_data.get_object_reference(
            'sale_crm_extension',
            'group_chef_service_administration_vente')[
            1]
        group_id = group_obj.browse(model_id)
        group_users.append(group_id.users)

        for user in group_users:
            for usr in user:
                followers = '%s;%s' % (usr.login, followers)

        self.mail_followers_plan_tour = followers
        print('Mails:', followers)

    mail_destination = fields.Char('Adresse mails', compute=_get_mail_destination)
    mail_followers_plan_tour = fields.Char('Adresse mails', compute=_get_followers_plan_tour)
    url_link = fields.Char("Lien", compute=_get_url_direct_link)

    def send_mail(self, email_id):
        template_id = self.env['ir.model.data'].get_object_reference('sale_crm_extension', email_id)
        try:
            mail_templ = self.env['mail.template'].browse(template_id[1])
            result = mail_templ.send_mail(res_id=self.id, force_send=True)
            print('result % ', result)
            return True
        except Exception as e:
            print('>>>> errror', str(e))
            return False

    def action_close_dialog(self):
        for activity in self:
            if activity.res_model == 'res.partner':
                partner = self.env['res.partner'].search([('id', '=', activity.res_id)])
                # Mettre à jour l'activité en rajoutant la ville et le nom du partenaire
                activity.write({
                    'city': partner.city,
                    'partner_name': partner.name,
                })
            if activity.res_model == 'sale.order':
                order = self.env['sale.order'].search([('id', '=', activity.res_id)])
                # Mettre à jour l'activité en rajoutant la ville et le nom du partenaire
                activity.write({
                    'city': order.partner_id.city,
                    'partner_name': order.partner_id.name,
                })
            if activity.res_model == 'crm.lead':
                crm_lead = self.env['crm.lead'].search([('id', '=', activity.res_id)])
                # Mettre à jour l'activité en rajoutant la ville et le nom du partenaire
                activity.write({
                    'city': crm_lead.partner_id.city,
                    'partner_name': crm_lead.partner_id.name,
                })
                self.send_mail('sale_crm_extension_send_mail_template')
                self.env['mail.activity.history'].create({
                    'activity_type_id': activity.activity_type_id.id if activity.activity_type_id else False,
                    'summary': activity.summary,
                    'note': activity.note,
                    'date_deadline': activity.date_deadline,
                    'user_id': activity.user_id.id if activity.user_id else False,
                    'state': activity.state,
                    'lead_id': activity.res_id,
                })
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Opportunity',
                    'res_model': 'crm.lead',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': activity.res_id,
                    'view_id': self.env.ref('crm.crm_lead_view_form').id,
                    'views': [(self.env.ref('crm.crm_lead_view_form').id, 'form')]
                }

    def compute_plan_auto(self):
        attachment_ids = []
        ir_cron = self.env.ref("sale_crm_extension.ir_cron_tour_plan_auto")
        lastcall = ir_cron.lastcall.strftime("%Y-%m-%d")
        nextcall = ir_cron.nextcall.strftime("%Y-%m-%d")
        data = {
            'date_from': lastcall,
            'date_to': nextcall,
        }
        detailled_plan_attachment_id = self.env['ir.attachment'].create({
            'name': "Plan de tournées detaillé",
            'type': 'binary',
            'datas': base64.b64encode(self.env.ref('sale_crm_extension.action_tour_plan')._render_qweb_pdf(self, data=data)[0]),
            'name': "Plan de tournées detaillé" + '.pdf',
            'store_fname': "Plan de tournées detaillé",
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        attachment_ids.append(detailled_plan_attachment_id)
        consolidated_tour_plan_attachment_id = self.env['ir.attachment'].create({
            'name': "Plan de tournées consolidé",
            'type': 'binary',
            'datas': base64.b64encode(self.env.ref('sale_crm_extension.action_consolidated_tour_plan')._render_qweb_pdf(self, data=data)[0]),
            'name': "Plan de tournées consolidé" + '.pdf',
            'store_fname': "Plan de tournées consolidé",
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        attachment_ids.append(consolidated_tour_plan_attachment_id)
        if attachment_ids:
            template_id = self.env.ref('sale_crm_extension.sale_crm_extension_send_mail_tour_plan').id
            try:
                mail_templ = self.env['mail.template'].browse(template_id)
                for attachment_id in attachment_ids:
                    mail_templ.attachment_ids = [(4, attachment_id.id)]
                mail_id = mail_templ.send_mail(self.id, force_send=True)
                for attachment_id in attachment_ids:
                    mail_templ.attachment_ids = [(3, attachment_id.id)]
                print('result % ', mail_id)
                return True
            except Exception as e:
                print('>>>> errror', str(e))
                return False


class MailActivityHistory(models.Model):
    _name = 'mail.activity.history'

    activity_type_id = fields.Many2one(
        'mail.activity.type', string='Activity Type',
        domain="['|', ('res_model_id', '=', False), ('res_model_id', '=', res_model_id)]", ondelete='restrict')

    summary = fields.Char('Summary')
    note = fields.Html('Note', sanitize_style=True)
    date_deadline = fields.Date('Due Date', index=True, required=True, default=fields.Date.context_today)

    user_id = fields.Many2one(
        'res.users', 'Assigned to',
        default=lambda self: self.env.user,
        index=True, required=True)

    state = fields.Selection([
        ('overdue', 'Overdue'),
        ('today', 'Today'),
        ('planned', 'Planned')], 'State')

    lead_id = fields.Many2one('crm.lead', string='Opportunité')