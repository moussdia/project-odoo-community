# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SaleContract(models.Model):
    _name = 'sale.contract'
    _rec_name = 'customer_id'
    _inherit = 'mail.thread', 'mail.activity.mixin'

    def action_submit_in_progress(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_progress'

    def action_submit_in_expired(self):
        for rec in self:
            if rec.state == 'in_progress':
                rec.state = 'expired'

    def action_submit_in_draft(self):
        for rec in self:
            if rec.state == 'in_progress':
                rec.state = 'draft'

    @api.onchange('order_number')
    def _get_customer_order_number(self):
        customer_order_number = self.env['sale.order'].browse([(self.order_number.id)])
        if customer_order_number:
            self.order_amount = customer_order_number.amount_total
        return

    def action_print(self):
        """
        Print report sale contract
        :return:
        """
        return self.env.ref('sale_crm_extension.action_print_contract').report_action(self)

    customer_id = fields.Many2one('res.partner', 'Client')
    order_number = fields.Many2one('sale.order', string='N° commande')
    order_object = fields.Char('Objet du contrat')
    order_amount = fields.Integer('Montant', compute=_get_customer_order_number, store=True)
    start_date = fields.Date('Début contrat')
    end_date = fields.Date('Fin contrat')
    state = fields.Selection([('draft', 'Brouillon'),
                              ('in_progress', 'En cours'),
                              ('expired', 'Expiré')], default="draft")
    alarm_id = fields.Many2one('calendar.alarm', 'Rappel')
    recipients_mails = fields.Char('Diffusion email', )

    @api.model
    def compute_expire_contract_auto(self):
        """
        Send notification to customer who contract expired
        :return:
        """
        self._get_recipients_mails()
        contracts = self.env['sale.contract'].search([('state', '=', 'in_progress')])
        print('contracts', contracts)
        if contracts:
            for contract in contracts:
                if contract.alarm_id:
                    if contract.alarm_id.alarm_type == 'email':
                        days = relativedelta(datetime.now().date(),
                                             fields.Datetime.from_string(contract.end_date)).days
                        print('days %s' % days)
                        if days <= contract.alarm_id.duration:
                            result = self.send_notification(contract.id)
        return True

    def send_notification(self, res_id):
        template_id = self.env.ref('sale_crm_extension.sale_contract_expire_send_mail_template')
        try:
            result = template_id.send_mail(res_id=res_id, force_send=True)
            return True
        except:
            return False

    def _get_recipients_mails(self):
        email = ''
        contracts = self.env['sale.contract'].search([('state', '=', 'in_progress')])
        print('contracts', contracts)
        if contracts:
            for contract in contracts:
                print('contract %s ' % contract)
                if contract.customer_id:
                    if contract.customer_id.email:
                        email += contract.customer_id.email + ';'
            self.recipients_mails = email
