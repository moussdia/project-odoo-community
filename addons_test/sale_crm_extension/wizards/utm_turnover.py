# -*- coding: utf-8 -*-
import base64
from odoo import fields, models, api
from datetime import datetime


class TourPlan(models.TransientModel):
    _name = 'utm.turnover.wizard'

    indicators = fields.Selection([
        ('turnover', 'Chiffre d\'affaires'),
        ('turnover_achieved_in_relation_to_the_objective', 'Chiffre d\'affaire réalisé par rapport à l\'objectif'),
        ('turnover_by_product_family', 'Chiffre d\'affaire réalisé par famille de produits'),
        ('turnover_achieved_by_customer_segment', 'Chiffre d\'affaire réalisé par segment de clients'),
        ('turnover_achieved_by_region_or_zone', 'Chiffre d\'affaire réalisé par région ou zone')
    ], 'Indicateurs de suivi', default='turnover')

    def action_turnover_print(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'indicators': self.indicators,
        }
        return self.env.ref('sale_crm_extension.action_turnover_for_the_current_month').report_action(self, data=data)


class ReportTourPlan(models.AbstractModel):
    _name = 'report.sale_crm_extension.report_turnover_for_the_current_month'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        turnover_for_the_current_month_docs = []
        cumulative_turnover_to_date_docs = []
        current_year_turnover_docs = []
        seller_users = []
        turnover_for_one_year_ago = []
        current_sale_year = []
        geographical_area = []

        if data['indicators'] == 'turnover':
            # Turnover for the current month
            turnover_for_the_current_month_cursor = self.env.cr
            turnover_for_the_current_month_cursor.execute("""
                                                            SELECT
                                                                SUM(sale_order.amount_untaxed)
                                                            FROM
                                                                sale_order
                                                            WHERE extract(year from sale_order.date_order) = %s    
                                                            AND extract(month from sale_order.date_order) = %s
                                                            AND sale_order.state = 'sale'
                                                        """ % (datetime.now().year, datetime.now().month))

            for indicator in turnover_for_the_current_month_cursor.fetchall():
                turnover_for_the_current_month_docs.append(indicator)

            # Total turnover achieved to date
            cumulative_turnover_to_date_cursor = self.env.cr
            cumulative_turnover_to_date_cursor.execute("""
                                                        SELECT
                                                            SUM(sale_order.amount_untaxed)
                                                        FROM
                                                            sale_order
                                                        WHERE sale_order.state = 'sale'    
                                                    """)

            for indicator in cumulative_turnover_to_date_cursor.fetchall():
                cumulative_turnover_to_date_docs.append(indicator)

            # Increase in turnover compared to year n-1
            current_year_turnover_cursor = self.env.cr
            current_year_turnover_cursor.execute("""
                                                    SELECT
                                                        SUM(sale_order.amount_untaxed)
                                                    FROM
                                                        sale_order
                                                    WHERE extract(year from sale_order.date_order) = %s
                                                    AND sale_order.state = 'sale' 
                                                """ % (datetime.now().year))

            for indicator in current_year_turnover_cursor.fetchall():
                current_year_turnover_docs.append(indicator)

            cursor_turnover_for_one_year_ago = self.env.cr
            cursor_turnover_for_one_year_ago.execute("""
                                                        SELECT
                                                            SUM(sale_order.amount_untaxed)
                                                        FROM
                                                            sale_order
                                                        WHERE extract(year from sale_order.date_order) = %s
                                                        AND sale_order.state = 'sale'
                                                    """ % (int(datetime.now().year) - 1))

            for indicator in cursor_turnover_for_one_year_ago.fetchall():
                turnover_for_one_year_ago.append(indicator)

        elif data['indicators'] == 'turnover_by_product_family':
            cursor = self.env.cr
            cursor.execute("""
                            SELECT
                                category.name,
                                SUM(sale_order_line.price_unit)
                            FROM
                                sale_order_line
                            INNER JOIN product_template AS product
                            ON product.id = sale_order_line.product_id
                            INNER JOIN product_category AS category
                            ON category.id = product.categ_id
                            GROUP BY
                                category.name
                            """)

            for indicator in cursor.fetchall():
                docs.append(indicator)

        elif data['indicators'] == 'turnover_achieved_in_relation_to_the_objective':
            sellers = self.env['res.users'].search([])

            for user in sellers:
                if user.has_group('sale_crm_extension.group_commercial'):
                    seller_users.append(user)

            current_sale_year = self.env['sale.year'].search([
                ('current_year', '=', datetime.now().year)
            ])

            docs = self.env['sale.goal.line'].search([
                ('year_id', '>=', current_sale_year[0].id)
            ])

        elif data['indicators'] == 'turnover_achieved_by_customer_segment':
            cursor_customer_segment = self.env.cr
            cursor_customer_segment.execute("""
                                            SELECT
                                                lead.customer_category,
                                                SUM(sale_order_history.amount_untaxed) as sum_amount
                                            FROM
                                                sale_order_history
                                            INNER JOIN crm_lead AS lead
                                            ON lead.id = sale_order_history.lead_id
                                            GROUP BY
                                                lead.customer_category
                                            """)

            for export in cursor_customer_segment.fetchall():
                docs.append(export)

        elif data['indicators'] == 'turnover_achieved_by_region_or_zone':
            areas = self.env['localization.zone'].search([])

            for area in areas:
                geographical_area.append(area)

            cursor_geographical_area = self.env.cr
            cursor_geographical_area.execute("""
                                            SELECT
                                                lead.geolocalisation,
                                                SUM(sale_order_history.amount_untaxed) as sum_amount
                                            FROM
                                                sale_order_history
                                            INNER JOIN crm_lead AS lead
                                            ON lead.id = sale_order_history.lead_id
                                            GROUP BY
                                                lead.geolocalisation
                                            """)

            for export in cursor_geographical_area.fetchall():
                docs.append(export)

        return {
            'indicators': data['indicators'],
            'records': docs,
            'turnover_for_one_year_ago': turnover_for_one_year_ago,
            'seller_users': seller_users,
            'current_sale_year': current_sale_year,
            'geographical_area': geographical_area,
            'turnover_for_the_current_month_docs': turnover_for_the_current_month_docs,
            'cumulative_turnover_to_date_docs': cumulative_turnover_to_date_docs,
            'current_year_turnover_docs': current_year_turnover_docs,
        }

