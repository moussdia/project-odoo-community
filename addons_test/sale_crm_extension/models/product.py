# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    type_id = fields.Many2one('product.category.type', 'Type catégorie', index=True, ondelete='cascade')


class ProductTypeCategory(models.Model):
    _name = "product.category.type"
    _description = "Product Category Type"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'
    _order = 'complete_name'

    name = fields.Char('Nom du type de catégorie', index=True, required=True)
    complete_name = fields.Char(
        'Nom complet', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one('product.category.type', 'Type parent', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    category_ids = fields.One2many('product.category', 'type_id', 'Catégories')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for type_category in self:
            if type_category.parent_id:
                type_category.complete_name = '%s / %s' % (type_category.parent_id.complete_name, type_category.name)
            else:
                type_category.complete_name = type_category.name
