# -- coding: utf-8 --
from datetime import datetime

from odoo import fields, models, api, _


class SaleGoal(models.Model):
    _name = 'sale.goal'
    _rec_name = 'name'

    name = fields.Char("Nom", required=True, translate=True)
    description = fields.Text("Description")
    user_id = fields.Many2one('res.users', 'Commercial', index=True, tracking=True, default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team', 'Equipe commerciale',
                              default=lambda self: self._default_team_id(self.env.uid),
                              index=True, tracking=True, )
    year_id = fields.Many2one('sale.year', 'Exercice commerciale')
    goal_line_ids = fields.One2many('sale.goal.line', 'goal_id', string='Lignes')

    def _default_team_id(self, user_id):
        return self.env['crm.team']._get_default_team_id(user_id=user_id)

    # def compute_goals_auto(self):
    #     """
    #     Compute goals
    #     :return:
    #     """
    #     period_id = self.env['sale.periodicity'].search([('state', '=', 'open')])
    #     print('open period', period_id)
    #     if period_id:
    #         goal_ids = self.env['sale.goal'].search([('year_id', '=', period_id.year_id.id)])
    #         if goal_ids and len(goal_ids) != 0:
    #             target_goal_volume = self.env['sale.goal.line'].search([('period_id', '=', period_id.id)])
    #             target_goal_value = self.env['sale.goal.line'].search([('period_id', '=', period_id.id)])
    #
    #             for goal in goal_ids:
    #                 current_goal_volume = self.env['crm.lead'].search_count([('user_id', '=', goal.user_id.id)])
    #
    #                 order_ids = self.env['sale.order'].search(
    #                     [('state', '=', 'sale'), ('user_id', '=', goal.user_id.id)])
    #                 current_goal_value = sum(o.amount_untaxed for o in order_ids)
    #
    #                 res = self.env['sale.goal.line'].search([('period_id', '=', period_id.id)]).write({
    #                     'current_goal_volume': current_goal_volume,
    #                     'current_goal_value': current_goal_value,
    #                 })


class SaleGoalLine(models.Model):
    _name = 'sale.goal.line'
    _rec_name = 'period_id'

    year_id = fields.Many2one('sale.year', 'Exercice')
    goal_id = fields.Many2one('sale.goal', 'Objectif')
    period_id = fields.Many2one('sale.periodicity', 'Période')
    start_date = fields.Date('Date de début', related='period_id.start_date', store=True, readonly=True)
    end_date = fields.Date('Date de fin', related='period_id.end_date', store=True, readonly=True)
    last_update = fields.Date('Dernière mise à jour', default=fields.Date.context_today)
    target_goal_volume = fields.Float('Objectif en volume', help="Objectif en volume")
    target_goal_value = fields.Float('Objectif en Chiffre d’affaire', help="Objectif en Chiffre d’affaire")
    current_goal_volume = fields.Float('Volume réalisé', help="Volume réalisé", compute='_generate_current_goal_volume')
    current_goal_value = fields.Float('Chiffre d’affaire réalisé', help="Chiffre d’affaire réalisé")
    rate_goal_volume = fields.Float('Taux de conversion en volume', help="Taux de conversion en volume", compute='_generate_rate_goal_volume')
    rate_goal_value = fields.Float('Taux de conversion en valeur', help="Taux de conversion en valeur", compute='_generate_rate_goal_value')
    rate_goal_productivity = fields.Float('Taux de productivité', compute='_generate_goal_productivity')
    user_id = fields.Many2one('res.users', 'Commercial', related='goal_id.user_id')

    def _generate_current_goal_volume(self):
        for line in self:
            leads_ids = self.env['crm.lead'].search([('year_id', '=', line.year_id.id),
                                                     ('user_id', '=', line.user_id.id),
                                                     ('period_id', '=', line.period_id.id),
                                                     ('step', '=', 'order_ongoing')])
            line.current_goal_volume = len(leads_ids)

    @api.depends('current_goal_volume', 'target_goal_volume')
    def _generate_rate_goal_volume(self):
        for volume in self:
            if volume.current_goal_volume != 0 and volume.target_goal_volume != 0:
                volume.rate_goal_volume = volume.current_goal_volume * 100 / volume.target_goal_volume
            else:
                volume.rate_goal_volume = 0

    @api.depends('current_goal_value', 'target_goal_value')
    def _generate_rate_goal_value(self):
        for value in self:
            if value.current_goal_value != 0 and value.target_goal_value != 0:
                value.rate_goal_value = (value.current_goal_value * 100) / value.target_goal_value
            else:
                value.rate_goal_value = 0

    @api.depends('rate_goal_value', 'rate_goal_volume')
    def _generate_goal_productivity(self):
        for rate in self:
            if rate.rate_goal_value != 0 and rate.rate_goal_volume != 0:
                rate.rate_goal_productivity = rate.rate_goal_value / rate.rate_goal_volume
                print('rate.rate_goal_value', rate.rate_goal_productivity)
            else:
                rate.rate_goal_productivity = 0



