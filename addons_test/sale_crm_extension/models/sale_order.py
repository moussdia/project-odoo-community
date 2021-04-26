# -- coding: utf-8 --
from urllib.parse import urljoin

import werkzeug

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from num2words import num2words


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    expense_ids = fields.One2many('sale.order.expense', 'order_id', 'Charges')
    evaluation_id = fields.Many2one('sale.order.evaluation', 'Evaluation')
    quality_of_service = fields.Char('Qualité du service')
    expense_total = fields.Float('Total', compute='_expense_total', store=True)
    comments = fields.Text('Commentaire')

    team_id = fields.Many2one('crm.team', 'Equipe commerciale')
    year_id = fields.Many2one('sale.year', 'Exercice commercial', domain=[('state', '=', 'open')], required=True)
    period_id = fields.Many2one('sale.periodicity', 'Periode commerciale', required=True)
    estimated_order_date = fields.Date('Date prévisionnelle de commande', required=True)
    refuse_raison = fields.Char('Raison du réfus', track_visibility='onchange')
    discount_note = fields.Char('Raison du réfus', track_visibility='onchange')
    dcm_discount_note = fields.Char('Raison du réfus DCM', track_visibility='onchange')
    dga_discount_note = fields.Char('Raison du réfus DGA', track_visibility='onchange')
    steps = fields.Selection([('suspect', 'Suspect'),
                              ('prospect', 'Prospect'),
                              ('analyse', 'Analyse'),
                              ('negociation', 'Négociation'),
                              ('standby', 'Standby'),
                              ('closing', 'Closing'),
                              ('order_ongoing', 'Order')], 'Etape')
    state = fields.Selection([
        ('draft', 'Devis à valider'),
        ('submitted', 'Devis à valider'),
        ('validated', 'Devis validé'),
        ('discount_chef_service_com_validated', 'Remise en attente de validation du Chef de Service Commercial'),
        ('discount_dcm_validated', 'Remise en attente de validation DCM'),
        ('discount_dga_validated', 'Remise en attente de validation DGA'),
        ('discount_validated', 'Remise validée'),
        ('sent', 'Devis envoyé'),
        ('sale', 'Bon de commande'),
        ('done', 'Terminé'),
        ('cancel', 'Annulé'),
    ], string='Etat', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    discount = fields.Float('Remise', default=0.0, compute='getDiscount', store=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Commercial', index=True,
        track_visibility='onchange', default=_default_employee)
    responsible_discount = fields.Boolean('Resp. Remise', default=False)
    lead_id = fields.Many2one('crm.lead', 'Lead')
    lead_state = fields.Selection([('suspect', 'Suspect'),
                                   ('prospect', 'Prospect'),
                                   ('analyse', 'Analyse'),
                                   ('negociation', 'Négociation'),
                                   ('closing', 'Closing'),
                                   ('order_ongoing', 'Order')], 'Etape', related='lead_id.step', store=True)
    technical_fees = fields.Float('Frais technique', default=25)
    technical_fees_ttc = fields.Float('Frais technique', compute='_get_technical_fees', store=True)
    rigor = fields.Float('Rigueur', default=40)
    # net_to_pay = fields.Monetary('Net à payer', compute='_get_total_amount_untaxed')
    wording = fields.Char('Libellé')
    fm = fields.Char('FM DU')
    recipients_mails = fields.Char('Diffusion email', compute='_get_mail_destination')
    payment_condition = fields.Char("Condition de règlement")

    total_amount_ht = fields.Monetary('Montant HT', compute='_get_total_amount_untaxed')
    total_amount_tax = fields.Monetary('Taxe', compute='_get_total_amount_untaxed')
    total_amount_ttc = fields.Monetary('Total', compute='_get_total_amount_untaxed')
    tsp = fields.Monetary('TSP3%', compute='_get_total_amount_untaxed')
    text_amount = fields.Char('Text Amount')
    applicable_tsp = fields.Float('TSP', default=3)

    @api.depends('amount_untaxed', 'technical_fees_ttc')
    def _get_total_amount_untaxed(self):
        self.total_amount_tax = 0
        self.total_amount_ttc = 0
        for rec in self:
            ht = rec.amount_untaxed + rec.technical_fees_ttc
            rec.total_amount_ht = ht
            for line in rec.order_line:
                tax = (line.tax_id.amount * ht) / 100
                tsp = (ht * rec.applicable_tsp) / 100
                ttc = ht + tax + tsp
                rec.total_amount_tax = tax
                rec.tsp = tsp
                rec.total_amount_ttc = round(ttc, 0)
                rec.text_amount = num2words(rec.total_amount_ttc, lang='fr')

    @api.depends('amount_untaxed', 'technical_fees')
    def _get_technical_fees(self):
        for rec in self:
            rec.technical_fees_ttc = (sum(line.price_unit for line in rec.order_line) * rec.technical_fees) / 100

    @api.depends('order_line', 'order_line.discount')
    def getDiscount(self):
        for rec in self:
            if rec.order_line:
                rec.discount = max(line.discount for line in rec.order_line)

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({'year_id': self.year_id.id,
                    'period_id': self.period_id.id,
                    'technical_fees': self.technical_fees,
                    'applicable_tsp': self.applicable_tsp,
                    'technical_fees_ttc': self.technical_fees_ttc,
                    'tsp': self.applicable_tsp,
                    'wording': self.wording,
                    'fm': self.fm,
                    })
        return res

    @api.depends('expense_ids')
    def _expense_total(self):
        for order in self:
            expense_total = 0
            for expense in order.expense_ids:
                expense_total += expense.amount
            order.expense_total = expense_total
        return

    def action_confirm(self):

        if self.partner_id.state != 'done':
            raise ValidationError(
                "Désolé, Vous ne pouvez pas confirmer le bon de commande car la création du client au sens "
                "comptable n'est pas encore effective")
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        """ overload table sale.goal.line"""
        goal_line_id = self.env['sale.goal.line'].search([('year_id', '=', self.year_id.id),
                                                          ('user_id', '=', self.user_id.id),
                                                          ('period_id', '=', self.period_id.id),
                                                          ])
        if goal_line_id:
            goal_line_id.write({
                'current_goal_value': self.amount_untaxed + goal_line_id.current_goal_value
            })
        return True

    def _get_url_direct_link(self):
        """
            génère l'url pour accéder directement au document en cours
        """
        res = {}
        res['view_type'] = 'form'
        res['model'] = 'sale.order'
        ir_menu_obj = self.env['ir.ui.menu']
        try:
            menu_ref_id = self.env['ir.model.data'].get_object_reference('sale_crm', 'sale_order_menu_quotations_crm')
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
        model_id = False
        followers = ''
        ir_model_data = self.env['ir.model.data']
        group_obj = self.env['res.groups']

        # Workflow à l'état brouillon
        if self.state == 'draft':
            model_id = ir_model_data.get_object_reference('sale_crm_extension', 'group_chef_service_commercial')[1]

        # Workflow au niveau du chef de service commercial
        if self.state == 'discount_chef_service_com_validated':
            model_id = ir_model_data.get_object_reference('sale_crm_extension', 'group_marketing_director')[1]

        # Workflow au niveau du DCM
        if self.state == 'discount_dcm_validated':
            model_id = ir_model_data.get_object_reference('sale_crm_extension', 'group_sub_director')[1]

        group_id = group_obj.browse(model_id)
        for user in group_id.users:
            followers = '%s;%s' % (user.login, followers)

        self.recipients_mails = followers
        print('Mails:', followers)

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

    def action_submit_for_validation(self):
        for rec in self:
            rec._get_mail_destination()
            rec.send_mail('sale_order_quotation_send_mail')
            rec.state = 'submitted'

    def action_validate_quotation(self):
        self.state = 'discount_chef_service_com_validated'
        if self.discount <= 5:
            self.state = 'discount_validated'

    def action_validate_discount(self):
        for record in self:
            if 6 <= record.discount <= 15:
                record.state = 'discount_validated'

            if record.discount > 15:
                record._get_mail_destination()
                record.send_mail('sale_order_quotation_send_mail')
                record.state = 'discount_dcm_validated'

    def action_validate_dcm_discount(self):
        for records in self:
            if records.discount > 25:
                records._get_mail_destination()
                records.send_mail('sale_order_quotation_send_mail')
                records.state = 'discount_dga_validated'
            else:
                records.state = 'discount_validated'

    def action_validate_dga_discount(self):
        self.state = 'discount_validated'

    @api.model
    def create(self, values):
        """Override default Odoo create function and extend."""
        res = super(SaleOrder, self).create(values)
        if res:
            print('Opportunity_id', res.opportunity_id)
            if res.opportunity_id:
                history = self.env['sale.order.history']
                history.create({
                    'name': res.name,
                    'amount_untaxed': res.amount_untaxed,
                    'comments': res.comments,
                    'lead_id': res.opportunity_id.id,
                })
        return res


class SaleOrderHistory(models.Model):
    _name = 'sale.order.history'

    name = fields.Char('Référence')
    amount_untaxed = fields.Float('Montant')
    evaluation_id = fields.Many2one('sale.order.evaluation', 'Evaluation')
    lead_id = fields.Many2one('crm.lead', string='Piste/Opportunité',
                              default={'lead_id': lambda self, cr, uid, context: context.get(
                                  'lead_id', False), })
    comments = fields.Text('Commentaire')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    quality_of_service = fields.Selection([('bad', 'Mauvaise'),
                                           ('way', 'Moyenne'),
                                           ('well', 'Bonne')], string='Qualité du service')
    price_unit = fields.Float('Prix unitaire', related="product_template_id.list_price", store=True)
