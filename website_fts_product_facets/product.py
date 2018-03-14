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

class fts_fts(models.Model):
    _inherit = 'fts.fts'

    facet = fields.Selection(selection_add=[('product_facets','Product Facet')])

    @api.one
    def get_object(self, words):
        if self.res_model == 'product.facet.value':
            facets = self.env['product.facet.value'].browse(self.res_id)
            if facets:
                return {'name': facets.product_tmpl_id.name, 'body': self.get_text([facets.product_tmpl_id.name, facets.product_tmpl_id.description_sale], words)}
        return super(fts_fts, self).get_object()

class product_facet_value(models.Model):
    _name = 'product.facet.value'
    _inherit = ['product.facet.value', 'fts.model']

    _fts_fields = ['facet_id', 'product_tmpl_id']

    _fts_fields_d = [
        {'name': 'facet_name', 'weight': 'A', 'related': 'facet_id.name', 'related_table': 'product_template'},
        {'name': 'name', 'weight': 'A', 'related': 'product_tmpl_id.name', 'related_table': 'product_template'},
    ]
    
    _fts_trigger = fields.Boolean(string='Trigger FTS Update', help='Change this field to update FTS.', compute='_compute_fts_trigger', store=True)

    @api.depends('facet_id.name', 'name')
    @api.one
    def _compute_fts_trigger(self):
        # TODO: Trigger this update when relevant translations change.
        if self._fts_trigger:
            self._fts_trigger = True
        else:
            self._fts_trigger = False

    @api.one
    def _full_text_search_update(self):
        super(product_facet_line, self)._full_text_search_update()
        # TODO: Fix this code
        #~ for val in vals.get('value_ids'):
            #~ for value in self.env['product.facet.value'].browse(val[2]):
                #~ self.env['fts.fts'].create({'res_model': self._name,'res_id': self.id, 'name': '%.30s' % value.name,'count': 1,'facet': 'product_facets','rank': 10})

class product_facet_value(models.Model):
    _name = 'product.facet.line'

    @api.multi
    def fts_search_suggestion(self):
        """
        Return a search result for search_suggestion.
        """
        return {
            'res_id': self.id,
            'model_record': self._name,
            'name': self.name_get(),
            'blog_id': self.blog_id.id,
            'product_tmpl_id': self.product_tmpl_id.id,
            'product_name': self.product_tmpl_id.name_get(),
        }
