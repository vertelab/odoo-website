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

    facet = fields.Selection(selection_add=[('product_template','Product Template')])

    @api.one
    def get_object(self, words):
        if self.res_model == 'product.template':
            product = self.env['product.template'].browse(self.res_id)
            if product:
                return {'name': product.name, 'body': self.get_text([product.name, product.description_sale], words)}
        #~ elif self.res_model == 'product.product':
            #~ product = self.env['product.product'].browse(self.res_id)
            #~ return {'name': product.name, 'body': self.get_text([product.name, product.description_sale], words)}
        return super(fts_fts, self).get_object()


class product_template(models.Model):
    _inherit = 'product.template'

    @api.one
    @api.depends('website_published','name','description_sale')
    def _full_text_search_update(self):
        if self.website_published and self.active:
            self.env['fts.fts'].update_text(self._name,self.id,text=self.name+' '+self.description_sale,rank=0)
            #~ self.env['fts.fts'].update_text(self._name,self.id,text=self.author_id.name,facet='author',rank=int(self.ranking))
        self.full_text_search_update = ''

    full_text_search_update = fields.Char(compute="_full_text_search_update",store=True)


#~ class product_product(models.Model):
    #~ _inherit = 'product.product'

    #~ @api.one
    #~ @api.depends('website_published','name','description_sale','product_templ_id')
    #~ def _full_text_search_update(self):
        #~ if self.website_published:
            #~ self.env['fts.fts'].update_html(self._name,self.id,html=self.content+' '+self.name+' '+self.subtitle,rank=int(self.ranking))
            #~ self.env['fts.fts'].update_text(self._name,self.id,text=self.author_id.name,facet='author',rank=int(self.ranking))
            #~ self.env['fts.fts'].update_text(self._name,self.id,text=self.blog_id.name,facet='blog',rank=int(self.ranking))
        #~ self.full_text_search_update = ''

    full_text_search_update = fields.Char(compute="_full_text_search_update",store=True)
