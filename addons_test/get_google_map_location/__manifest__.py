
# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015  TM_FULLNAME
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
###############################################################################
{
    "name": "Partner Google Map",
    "version": "1.0",
    "category": "Extra Tools",
    "summary": "Map widget",
    "description": """Google Maps widget for Prtners""",
    "author": "CodersFort",
    "license": "AGPL-3",
    "website": "http://www.codersfort.com",
    "sequence": 0,
    "images": ["images/parner_google_map_location.png"],
    "depends": ["base","base_setup"],
    "qweb": [
        "static/src/xml/web_map.xml",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/web_map_templates.xml",
        "views/res_config_views.xml",
        "wizard/set_google_map_location.xml"
    ],
    "installable": True,
}
