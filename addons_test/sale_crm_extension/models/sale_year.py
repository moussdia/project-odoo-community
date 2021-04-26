# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from datetime import datetime

from odoo.exceptions import ValidationError


class SaleYear(models.Model):
    _name = 'sale.year'
    _description = 'Exercice commercial'
    _rec_name = 'name'

    name = fields.Char('Nom')
    start_date = fields.Date('Date début')
    end_date = fields.Date('Date fin')
    period_ids = fields.One2many('sale.periodicity', 'year_id', string='Période commerciale')
    state = fields.Selection([('draft', 'Brouillon'),
                              ('open', 'En cours'),
                              ('close', 'Terminé')], default='draft')
    appear_button = fields.Boolean('Active', default=False)
    current_year = fields.Integer('Academic Year', default=datetime.now().year)
    goal_count = fields.Integer(compute='_goal_count', string='# Objectifs')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        '''
        Check interleaving between sale years.
        There are 3 cases to consider:
        '''

        for sy in self:
            # Starting date must be prior to the ending date
            start_date = sy.start_date
            end_date = sy.end_date
            if end_date < start_date:
                raise ValidationError(_('La date de fin ne doit pas être antérieure à la date de début.'))

            domain = [
                ('id', '!=', sy.id),
                '|', '|',
                '&', ('start_date', '<=', sy.start_date), ('end_date', '>=', sy.start_date),
                '&', ('start_date', '<=', sy.end_date), ('end_date', '>=', sy.end_date),
                '&', ('start_date', '<=', sy.start_date), ('end_date', '>=', sy.end_date),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(_(
                    'Vous ne pouvez pas avoir de chevauchement entre deux exercices, veuillez corriger les dates de '
                    'début et / ou de fin de vos exercices.'))

    def action_generate_quarterly_periods(self):
        open_state = self.search([('state', '=',  'open')])
        if len(open_state) >= 1:
            raise ValidationError("Vous ne pouvez pas ouvrir plus de deux exercices à la fois!!")
        name1 = 'Q1'
        start_date1 = datetime.strptime('01/01/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date1 = datetime.strptime('31/03/' + str(self.current_year) + '', "%d/%m/%Y")
        name2 = 'Q2'
        start_date2 = datetime.strptime('01/04/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date2 = datetime.strptime('30/06/' + str(self.current_year) + '', "%d/%m/%Y")
        name3 = 'Q3'
        start_date3 = datetime.strptime('01/07/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date3 = datetime.strptime('30/09/' + str(self.current_year) + '', "%d/%m/%Y")
        name4 = 'Q4'
        start_date4 = datetime.strptime('01/10/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date4 = datetime.strptime('31/12/' + str(self.current_year) + '', "%d/%m/%Y")

        vals = [{
            'name': name1,
            'start_date': start_date1,
            'end_date': end_date1,
            'year_id': self.id,
        }, {
            'name': name2,
            'start_date': start_date2,
            'end_date': end_date2,
            'year_id': self.id,
        }, {
            'name': name3,
            'start_date': start_date3,
            'end_date': end_date3,
            'year_id': self.id,
        }, {
            'name': name4,
            'start_date': start_date4,
            'end_date': end_date4,
            'year_id': self.id,
        }]
        if len(self.period_ids) > 0:
            print(len(self.period_ids))
        else:
            self.env['sale.periodicity'].create(vals)
            self.state = 'open'

    def action_generate_monthly_periods(self):
        open_state = self.search([('state', '=', 'open')])
        if len(open_state) >= 1:
            raise ValidationError("Vous ne pouvez pas ouvrir plus de deux exercices à la fois!!")
        name1 = 'M1'
        start_date1 = datetime.strptime('01/01/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date1 = datetime.strptime('31/01/' + str(self.current_year) + '', "%d/%m/%Y")
        name2 = 'M2'
        start_date2 = datetime.strptime('01/02/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date2 = datetime.strptime('27/03/' + str(self.current_year) + '', "%d/%m/%Y")
        name3 = 'M3'
        start_date3 = datetime.strptime('01/03/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date3 = datetime.strptime('30/03/' + str(self.current_year) + '', "%d/%m/%Y")
        name4 = 'M4'
        start_date4 = datetime.strptime('01/04/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date4 = datetime.strptime('30/04/' + str(self.current_year) + '', "%d/%m/%Y")
        name5 = 'M5'
        start_date5 = datetime.strptime('01/05/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date5 = datetime.strptime('31/05/' + str(self.current_year) + '', "%d/%m/%Y")
        name6 = 'M6'
        start_date6 = datetime.strptime('01/06/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date6 = datetime.strptime('30/06/' + str(self.current_year) + '', "%d/%m/%Y")
        name7 = 'M7'
        start_date7 = datetime.strptime('01/07/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date7 = datetime.strptime('31/07/' + str(self.current_year) + '', "%d/%m/%Y")
        name8 = 'M8'
        start_date8 = datetime.strptime('01/08/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date8 = datetime.strptime('31/08/' + str(self.current_year) + '', "%d/%m/%Y")
        name9 = 'M9'
        start_date9 = datetime.strptime('01/09/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date9 = datetime.strptime('30/09/' + str(self.current_year) + '', "%d/%m/%Y")
        name10 = 'M10'
        start_date10 = datetime.strptime('01/10/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date10 = datetime.strptime('31/10/' + str(self.current_year) + '', "%d/%m/%Y")
        name11 = 'M11'
        start_date11 = datetime.strptime('01/11/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date11 = datetime.strptime('30/11/' + str(self.current_year) + '', "%d/%m/%Y")
        name12 = 'M12'
        start_date12 = datetime.strptime('01/12/' + str(self.current_year) + '', "%d/%m/%Y")
        end_date12 = datetime.strptime('31/12/' + str(self.current_year) + '', "%d/%m/%Y")
        vals = [{
            'name': name1,
            'start_date': start_date1,
            'end_date': end_date1,
            'year_id': self.id,
        }, {
            'name': name2,
            'start_date': start_date2,
            'end_date': end_date2,
            'year_id': self.id,
        }, {
            'name': name3,
            'start_date': start_date3,
            'end_date': end_date3,
            'year_id': self.id,
        }, {
            'name': name4,
            'start_date': start_date4,
            'end_date': end_date4,
            'year_id': self.id,
        }, {
            'name': name5,
            'start_date': start_date5,
            'end_date': end_date5,
            'year_id': self.id,
        }, {
            'name': name6,
            'start_date': start_date6,
            'end_date': end_date6,
            'year_id': self.id,
        }, {
            'name': name7,
            'start_date': start_date7,
            'end_date': end_date7,
            'year_id': self.id,
        }, {
            'name': name8,
            'start_date': start_date8,
            'end_date': end_date8,
            'year_id': self.id,
        }, {
            'name': name9,
            'start_date': start_date9,
            'end_date': end_date9,
            'year_id': self.id,
        }, {
            'name': name10,
            'start_date': start_date10,
            'end_date': end_date10,
            'year_id': self.id,
        }, {
            'name': name11,
            'start_date': start_date11,
            'end_date': end_date11,
            'year_id': self.id,
        }, {
            'name': name12,
            'start_date': start_date12,
            'end_date': end_date12,
            'year_id': self.id,
        }]

        if len(self.period_ids) > 0:
            print(len(self.period_ids))
        else:
            self.env['sale.periodicity'].create(vals)
            self.state = 'open'

    def action_generate_goals(self):
        """
        Generate sale goal of year record
        """
        team_ids = self.env['crm.team'].search([])
        for year in self:
            for team in team_ids:
                member_ids = team.member_ids
                for member in member_ids:
                    goal_obj = {
                        'team_id': team.id,
                        'user_id': member.id,
                        'year_id': year.id,
                        'name': 'Objectif ' + year.name + ' assigné à ' + member.name,
                    }
                    res = self.env['sale.goal'].create(goal_obj)

                    vals = []
                    if res:
                        for period in year.period_ids:
                            line_obj = {
                                'year_id': year.id,
                                'period_id': period.id,
                                'goal_id': res.id,
                            }
                            vals.append(line_obj)
                        self.env['sale.goal.line'].create(vals)
                        self.appear_button = True

    def action_close(self):
        for rec in self:
            rec.state = 'close'

    def _goal_count(self):
        for year in self:
            goal_ids = self.env['sale.goal'].sudo().search([('year_id', '=', year.id)])
            year.goal_count = len(goal_ids) if goal_ids else 0

    def goal_view(self):
        self.ensure_one()
        domain = [
            ('year_id', '=', self.id)]
        return {
            'name': _('Objectifs'),
            'domain': domain,
            'res_model': 'sale.goal',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                              Cliquez pour créer de nouveaux objectifs
                           </p>'''),
            'limit': 80,
            'context': "{'default_year_id': '%s'}" % (self.id)
        }
