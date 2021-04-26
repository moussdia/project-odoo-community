# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SetGoogleMapLocation(models.TransientModel):
    _name = 'set.google.map.location'

    @api.model
    def _get_partner_id(self):
        return self.env.context.get('active_id') or False

    partner_id = fields.Many2one('res.partner', 'Partner',readonly=True,default=_get_partner_id,ondelete='cascade')
    google_map_latitude =  fields.Char(string='Latitude',required=True)
    google_map_longitude =  fields.Char(string='Longitude',required=True)

    def change_location(self):
        active_id = self.env.context.get('active_id')
        res_partner_obj = self.env['res.partner'].sudo().search([('id','=',active_id)])
        google_map_latitude = self.google_map_latitude
        google_map_longitude = self.google_map_longitude
        if active_id:
            location = google_map_latitude + ',' + google_map_longitude
            res_partner_obj.write({
                'google_map_location': location,
            })
        else:
            raise ValidationError(_("Partner is not proper!"))
