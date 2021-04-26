# -*- coding: utf-8 -*-
import base64
from odoo import fields, models, api
from datetime import datetime


class TourPlan(models.TransientModel):
    _name = 'utm.sales.volume.wizard'

    indicators = fields.Selection([
        ('sales_volume', 'Volume des ventes'),
        ('volume_achieved_compared_to_target', 'Volume réalisé par rapport à l\'objectif'),
        ('volume_achieved_by_product_family', 'Volume réalisé par famille de produits'),
        ('volume_achieved_by_customer_segment', 'Volume réalisé par segment de clients'),
        ('volume_achieved_by_region_or_zone', 'Volume réalisé par région ou zone')
    ], 'Indicateurs de suivi', default='sales_volume')

    def action_sales_volume_print(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'indicators': self.indicators,
        }
        return self.env.ref('sale_crm_extension.action_sales_volume').report_action(self, data=data)


class ReportTourPlan(models.AbstractModel):
    _name = 'report.sale_crm_extension.report_sales_volume'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        volume_of_the_current_month_docs = []
        total_volume_achieved_to_date_docs = []
        sales_volume_current_year_docs = []
        seller_users = []
        sales_volume_for_one_year_ago = []
        current_sale_year = []
        geographical_area = []

        if data['indicators'] == 'sales_volume':
            volume_of_the_current_month_cursor = self.env.cr
            volume_of_the_current_month_cursor.execute("""
                            SELECT
                                COUNT(*)
                            FROM
                                sale_order
                            WHERE extract(year from sale_order.date_order) = %s    
                            AND extract(month from sale_order.date_order) = %s
                            AND sale_order.state = 'sale'
                            """ % (datetime.now().year, datetime.now().month))

            for indicator in volume_of_the_current_month_cursor.fetchall():
                volume_of_the_current_month_docs.append(indicator)

            total_volume_achieved_to_date_cursor = self.env.cr
            total_volume_achieved_to_date_cursor.execute("""
                            SELECT
                                COUNT(*)
                            FROM
                                sale_order
                            WHERE sale_order.state = 'sale'    
                            """)

            for indicator in total_volume_achieved_to_date_cursor.fetchall():
                total_volume_achieved_to_date_docs.append(indicator)

            sales_volume_current_year_cursor = self.env.cr
            sales_volume_current_year_cursor.execute("""
                            SELECT
                                COUNT(*)
                            FROM
                                sale_order
                            WHERE extract(year from sale_order.date_order) = %s
                            AND sale_order.state = 'sale' 
                            """ % (datetime.now().year))

            for indicator in sales_volume_current_year_cursor.fetchall():
                sales_volume_current_year_docs.append(indicator)

            cursor_sales_volume_for_one_year_ago = self.env.cr
            cursor_sales_volume_for_one_year_ago.execute("""
                            SELECT
                                COUNT(*)
                            FROM
                                sale_order
                            WHERE extract(year from sale_order.date_order) = %s
                            AND sale_order.state = 'sale'
                            """ % (int(datetime.now().year) - 1))

            for indicator in cursor_sales_volume_for_one_year_ago.fetchall():
                sales_volume_for_one_year_ago.append(indicator)

        elif data['indicators'] == 'volume_achieved_compared_to_target':
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

            print('docs', docs)
        elif data['indicators'] == 'volume_achieved_by_product_family':
            cursor = self.env.cr
            cursor.execute("""
                            SELECT
                                category.name,
                                COUNT(sale_order_line.id)
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

        elif data['indicators'] == 'volume_achieved_by_customer_segment':
            cursor_customer_segment = self.env.cr
            cursor_customer_segment.execute("""
                                            SELECT
                                                lead.customer_category,
                                                COUNT(sale_order_history.id) as count_volume
                                            FROM
                                                sale_order_history
                                            INNER JOIN crm_lead AS lead
                                            ON lead.id = sale_order_history.lead_id
                                            GROUP BY
                                                lead.customer_category
                                            """)

            for export in cursor_customer_segment.fetchall():
                docs.append(export)

        elif data['indicators'] == 'volume_achieved_by_region_or_zone':
            areas = self.env['localization.zone'].search([])

            for area in areas:
                geographical_area.append(area)

            cursor_geographical_area = self.env.cr
            cursor_geographical_area.execute("""
                                                SELECT
                                                    lead.geolocalisation,
                                                    COUNT(sale_order_history.id) as count_volume
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
            'sales_volume_for_one_year_ago': sales_volume_for_one_year_ago,
            'seller_users': seller_users,
            'current_sale_year': current_sale_year,
            'geographical_area': geographical_area,
            'volume_of_the_current_month_docs': volume_of_the_current_month_docs,
            'total_volume_achieved_to_date_docs': total_volume_achieved_to_date_docs,
            'sales_volume_current_year_docs': sales_volume_current_year_docs,
        }

