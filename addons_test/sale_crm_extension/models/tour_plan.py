# -*- coding: utf-8 -*-
import base64
from odoo import fields, models, api
from datetime import datetime


class TourPlan(models.TransientModel):
    _name = 'tour.plan'

    name = fields.Char('Nom')
