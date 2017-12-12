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

    facet = fields.Selection(selection_add=[('product_template','Product Template'), ('product_product','Product Product'), ('product_public_category','Product Public Category')])

    @api.one
    def get_object(self, words):
        if self.res_model == 'product.template':
            product = self.env['product.template'].browse(self.res_id)
            if product:
                return {'name': product.name, 'body': self.get_text([product.name, product.description_sale], words)}
        elif self.res_model == 'product.product':
            product = self.env['product.product'].browse(self.res_id)
            if product:
                return {'name': product.name, 'body': self.get_text([product.name, product.description_sale, product.default_code], words)}
        elif self.res_model == 'product.public.category':
            category = self.env['product.public.category'].browse(self.res_id)
            if category:
                return {'name': category.name, 'body': self.get_text([category.name], words)}
        return super(fts_fts, self).get_object()


class product_template(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'fts.model']

    _fts_fields = ['website_published', 'name', 'description_sale']

    @api.one
    def _full_text_search_update(self):
        super(product_template, self)._full_text_search_update()
        if self.website_published and self.active:
            self.env['fts.fts'].update_text(self._name, self.id, text=self.name, rank=0)
            if self.description_sale:
                self.env['fts.fts'].update_text(self._name, self.id, text=self.description_sale, rank=5)
            #~ self.env['fts.fts'].update_text(self._name,self.id,text=self.author_id.name,facet='author',rank=int(self.ranking))



class product_product(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'fts.model']

    _fts_fields = ['website_published','name','description_sale','default_code','product_tmpl_id','attribute_value_ids']

    @api.one
    def _full_text_search_update(self):
        super(product_product, self)._full_text_search_update()
        if self.website_published and self.active:
            self.env['fts.fts'].update_text(self._name, self.id, text=self.name, rank=0)
            self.env['fts.fts'].update_text(self._name, self.id, text=(self.description_sale or '')+' '+ ' '.join([att.name for att in self.attribute_value_ids]), rank=5)
            self.env['fts.fts'].update_text(self._name,self.id, text=self.default_code, rank=0)
            self.env['fts.fts'].update_text(self._name,self.id, text=self.ean13, rank=0)

class product_public_category(models.Model):
    _name = 'product.public.category'
    _inherit = ['product.public.category', 'fts.model']

    _fts_fields = ['name']

    @api.one
    def _full_text_search_update(self):
        super(product_public_category, self)._full_text_search_update()
        self.env['fts.fts'].update_text(self._name, self.id, text=self.name, rank=5)
