# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api


class SaleGoalReport(models.Model):
    """ Sale goal Analysis """

    _name = "sale.goal.report"
    _auto = False
    _description = "Sale goal Analysis"
    _rec_name = 'id'

    year_id = fields.Many2one('sale.year', 'Exercice', readonly=True)
    goal_id = fields.Many2one('sale.goal', 'Objectif', readonly=True)
    period_id = fields.Many2one('sale.periodicity', 'Période', readonly=True)
    start_date = fields.Date('Date de début', readonly=True)
    end_date = fields.Date('Date de fin', readonly=True)
    target_goal_volume = fields.Float('Objectif en volume', readonly=True)
    target_goal_value = fields.Float('Objectif en Chiffre d’affaire', readonly=True)
    current_goal_volume = fields.Float('Volume réalisé', help="Volume réalisé", readonly=True)
    current_goal_value = fields.Float('Chiffre d’affaire réalisé', readonly=True)
    rate_goal_volume = fields.Float('Taux de conversion en volume', readonly=True)
    rate_goal_value = fields.Float('Taux de conversion en valeur', readonly=True)
    rate_goal_productivity = fields.Float('Taux de productivité', readonly=True)
    name = fields.Char("Nom", readonly=True, )
    description = fields.Text("Description", readonly=True, )
    user_id = fields.Many2one('res.users', 'Commercial', readonly=True, )
    team_id = fields.Many2one('crm.team', 'Equipe commerciale', readonly=True, )

    # l.current_goal_volume,
    # l.rate_goal_volume,
    # l.rate_goal_value,
    # l.rate_goal_productivity,
    def _select(self):
        return """
            SELECT
                l.id,
                l.goal_id,
                l.year_id,
                l.period_id,
                l.start_date,
                l.end_date,
                l.target_goal_volume,
                l.target_goal_value,
                l.current_goal_value,  
                           
                g.user_id,
                g.team_id,
                g.name,
                g.description
        """

    def _from(self):
        return """
            FROM sale_goal_line AS l
        """

    def _join(self):
        return """
            JOIN sale_goal AS g ON l.goal_id = g.id
            JOIN sale_periodicity AS p ON l.period_id = p.id
            JOIN sale_year AS y ON l.year_id = y.id
            JOIN res_users AS u ON g.user_id = u.id
            JOIN crm_team AS t ON g.team_id = t.id
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join())
                         )
