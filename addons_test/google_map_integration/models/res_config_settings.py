# -*- coding: utf-8 -*-
# License AGPL-3
from odoo import api, fields, models



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

  

    google_maps_view_api_keys = fields.Char(string='Google Maps View Api Key',config_parameter='google.api_key_geocode')
    
