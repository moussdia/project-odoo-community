# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import math
import re

from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64, binascii
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
from odoo import fields, http, SUPERUSER_ID, tools, _


# --------------------------------------------------
# Misc tools
# --------------------------------------------------

class CustomerPortalCustom(CustomerPortal):
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name","partlat","partlong","searchInput"]

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        print("customized portal page for google map")
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        print("post",post)
        print("values",values)
        print("partner",partner)
        partlat = post.get('partlat')
        partlong=post.get('partlong')
        print("partlat",partlat)
        print("partlong",partlong)

        values.update({
            'error': {},
            'error_message': [],
        })    
        if post:
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)    
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                values.update({'zip': values.pop('zipcode', '')})
                if partlat and partlong:
                    values.update({'partner_latitude': partlat,
                                   'partner_longitude':partlong})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        apikeyobj= request.env['ir.config_parameter'].sudo().search([('key','=',"google.api_key_geocode")])
        print("apikeyobj.value",apikeyobj.value)
        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
            'google_maps_api_key':apikeyobj,
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

class WebsiteSale(ProductConfiguratorController):
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            print("button clicked")
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                print("post",post)
                print("kw",kw)
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        apikeyobj= request.env['ir.config_parameter'].sudo().search([('key','=',"google.api_key_geocode")])

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'google_maps_api_key':apikeyobj,
            
        }
        print("apikeyobj",apikeyobj.value)
        return request.render("website_sale.address", render_values)
    
    def _checkout_form_save(self, mode, checkout, all_values):
        print("_checkout_form_save",checkout)
        print("_checkout_form_savall",all_values)
        partner_lat=all_values.get('partlat')
        partner_long=all_values.get('partlong')
        print("partner_lat",partner_lat)
        checkout.update({'partner_latitude':partner_lat,
                        'partner_longitude':partner_long})
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = Partner.sudo().create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id