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

class product_facet_value(models.Model):
    _name = 'product.facet.value'
    _inherit = ['product.facet.value', 'fts.model']

    _fts_fields = ['facet_id', 'product_tmpl_id']

    def _get_fts_fields(self):
        return [
            {'name': 'facet_id.name', 'weight': 'B'},
            {'name': 'name', 'weight': 'A'},
        ]
    
    _fts_trigger = fields.Boolean(string='Trigger FTS Update', help='Change this field to update FTS.', compute='_compute_fts_trigger', store=True)

    @api.one
    def _full_text_search_update(self):
        pass

class product_product(models.Model):
    _inherit = 'product.product'

    def _get_fts_fields(self):
        return [
            {'name': 'facet_line_ids.facet_id.name', 'weight': 'C'},
            {'name': 'facet_line_ids.value_ids.name', 'weight': 'B'},
        ] + super(product_product, self)._get_fts_fields()

class product_template(models.Model):
    _inherit = 'product.template'

    def _get_fts_fields(self):
        return [
            {'name': 'facet_line_ids.facet_id.name', 'weight': 'C'},
            {'name': 'facet_line_ids.value_ids.name', 'weight': 'B'},
        ] + super(product_template, self)._get_fts_fields()
