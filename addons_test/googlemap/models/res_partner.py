# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re


class ResPartner(models.Model):
    _inherit = "res.partner"

    google_map_location = fields.Char(string='Google Map Location')

    def get_lat_long(self, latitude, longitude):
        active_id = self.env.context.get('active_id')
        res_partner_obj = self.env['res.partner'].search([('id', '=', active_id)])
        for record in self:
            if record.id:
                record.sudo().write({
                    'google_map_location': str(latitude) + ',' + str(longitude)
                })

    @api.model
    def get_default_google_maps_api_key(self):
        google_maps_api_key = self.env['ir.config_parameter'].get_param('google_maps_api_key', default='')
        return dict(google_maps_api_key=google_maps_api_key)

    def return_google_map_location(self):
        google_maps_api_key = self.env['ir.config_parameter'].get_param('google_maps_api_key', default='')
        res_partner_obj = self.env['res.partner'].search([('id', '=', self.id)])
        google_map_location = res_partner_obj.google_map_location
        return dict(google_map_location=google_map_location, google_maps_api_key=google_maps_api_key)
