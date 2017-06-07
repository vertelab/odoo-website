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

    facet = fields.Selection(selection_add=[('product_facet','Product Facet')])

    @api.one
    def get_object(self, words):
        if self.res_model == 'product.facet.line':
            facets = self.env['product.facet.line'].browse(self.res_id)
            if facets:
                return {'name': facets.product_tmpl_id.name, 'body': self.get_text([facets.product_tmpl_id.name, facets.product_tmpl_id.description_sale], words)}
        return super(fts_fts, self).get_object()


class product_facet_line(models.Model):
    _inherit = 'product.facet.line'

    @api.one
    @api.depends('facet_id','value_ids','product_tmpl_id')
    def _full_text_search_update(self):
        facets_values = ''
        if len(self.value_ids) > 0:
            for value in self.value_ids:
                    facets_values += ' %s' %value.name
        self.env['fts.fts'].update_text(self._name,self.id,text=self.facet_id.name+facets_values,rank=0)
        self.full_text_search_update = ''

    full_text_search_update = fields.Char(compute="_full_text_search_update",store=True)
