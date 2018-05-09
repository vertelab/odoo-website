# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2017- Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class product_template(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'fts.model']

    def _get_fts_fields(self):
        return [
            {'name': 'name', 'weight': 'A'},
            {'name': 'attribute_line_ids.value_ids.name', 'weight': 'A'},
            {'name': 'description_sale', 'weight': 'B'}]

    @api.model
    def fts_get_default_suggestion_domain(self):
        """
        Return the default domain for search suggestions.
        """
        return [('sale_ok', '=', True)]

class product_product(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'fts.model']

    def _get_fts_fields(self):
        return [
            {'name': 'name', 'weight': 'A', 'related': 'product_tmpl_id.name', 'related_table': 'product_template'},
            {'name': 'attribute_value_ids.name', 'weight': 'A'},
            {'name': 'description_sale', 'weight': 'B'},
            {'name': 'default_code', 'weight': 'A'},
            {'name': 'ean13', 'weight': 'A'}]
    _fts_trigger = fields.Boolean(string='Trigger FTS Update', help='Change this field to update FTS.', compute='_compute_fts_trigger', store=True)

    @api.model
    def fts_get_default_suggestion_domain(self):
        """
        Return the default domain for search suggestions.
        """
        return [('sale_ok', '=', True)]

    @api.multi
    def fts_search_suggestion(self):
        """
        Return a search result for search_suggestion.
        """
        return {
            'res_id': self.id,
            'model_record': self._name,
            'name': self.name_get()[0][1],
            'product_tmpl_id': self.product_tmpl_id.id
        }

class product_public_category(models.Model):
    _name = 'product.public.category'
    _inherit = ['product.public.category', 'fts.model']

    def _get_fts_fields(self):
        return [{'name': 'name', 'weight': 'A'}]
