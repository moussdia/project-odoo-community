# -- coding: utf-8 --
from urllib.parse import urljoin

import werkzeug
from num2words import num2words

from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    year_id = fields.Many2one('sale.year', 'Exercice commercial', store=True)
    period_id = fields.Many2one('sale.periodicity', 'Periode commerciale', store=True)
    technical_fees = fields.Float('Frais technique', store=True)
    applicable_tsp = fields.Float('TSP', store=True)
    technical_fees_ttc = fields.Float('Frais technique', store=True)
    tsp = fields.Monetary('TSP', store=True)
    user_email = fields.Char('Email', compute='_get_email')
    total_amount_ht = fields.Monetary('Montant HT', compute='_get_total_amount')
    total_amount_tax = fields.Monetary('Taxe', compute='_get_total_amount_untaxed')
    total_amount_ttc = fields.Monetary('Total', compute='_get_total_amount')
    wording = fields.Char('Libellé')
    fm = fields.Char('FM DU')
    text_amount = fields.Char('Text Amount')

    @api.depends('amount_total', 'technical_fees_ttc', 'tsp')
    def _get_total_amount(self):
        self.total_amount_tax = 0
        self.total_amount_ttc = 0
        for rec in self:
            ht = rec.amount_untaxed + rec.technical_fees_ttc
            rec.total_amount_ht = ht
            print('rec.total_amount_ht', rec.total_amount_ht)
            for line in rec.invoice_line_ids:
                tax = (line.tax_ids.amount * ht) / 100
                tsp = (ht * rec.applicable_tsp) / 100
                ttc = ht + tax + tsp
                rec.total_amount_tax = tax
                rec.tsp = tsp
                rec.total_amount_ttc = round(ttc, 0)
                rec.text_amount = num2words(rec.total_amount_ttc, lang='fr')

    def _get_email(self):
        for rec in self:
            rec.user_email = rec.user_id.login

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

    def action_post(self):
        self._get_mail_destination()
        self.send_mail('invoice_validated_send_mail')
        return self._post(soft=False)


class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    total_amount_ttc = fields.Monetary('Total TTC')
