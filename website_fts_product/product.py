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
    _fts_fields_d = [{'name': 'name'}, {'name': 'description_sale'}]

    @api.depends('name', 'description_sale')
    @api.one
    def _compute_fts_trigger(self):
        """
        Dummy field to trigger the updates on SQL level. Tracking
        changes is much easier on Odoo level than on SQL level. Make
        this field dependant on the relevant fields.
        """
        # TODO: Trigger this update when relevant translations change.
        _logger.warn('\n\n_compute_fts_trigger product.template')
        if self._fts_trigger:
            self._fts_trigger = True
        else:
            self._fts_trigger = False

    @api.one
    def _full_text_search_update(self):
        # TODO: Remove the context as it doesn't belong in a general purpose module.
        # This is starting to be a too comon problem. Probably should change the checks to only activate in certain views.
        super(product_template, self).with_context(suppress_checks=True)._full_text_search_update()
        self._full_text_search_delete()
        self.write({'fts_dirty': False})
        if self.website_published and self.active:
            self.env['fts.fts'].update_text(self._name, self.id, text=self.name, rank=0)
            if self.description_sale:
                self.env['fts.fts'].update_text(self._name, self.id, text=self.description_sale, rank=5)
            #~ self.env['fts.fts'].update_text(self._name,self.id,text=self.author_id.name,facet='author',rank=int(self.ranking))

class product_product(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'fts.model']

    _fts_fields = ['website_published','name','description_sale','default_code','ean13','product_tmpl_id','attribute_value_ids']
    _fts_fields_d = [{'name': 'name', 'related': 'product_tmpl_id.name', 'related_table': 'product_template'}, {'name': 'description_sale'}, {'name': 'default_code'}, {'name': 'ean13'}]

    _fts_trigger = fields.Boolean(string='Trigger FTS Update', help='Change this field to update FTS.', compute='_compute_fts_trigger', store=True)

    @api.depends('product_tmpl_id.name', 'description_sale', 'default_code', 'ean13')
    @api.one
    def _compute_fts_trigger(self):
        """
        Dummy field to trigger the updates on SQL level. Tracking
        changes is much easier on Odoo level than on SQL level. Make
        this field dependant on the relevant fields.
        """
        _logger.warn('\n\n_compute_fts_trigger product.product')
        # TODO: Trigger this update when relevant translations change.
        if self._fts_trigger:
            self._fts_trigger = True
        else:
            self._fts_trigger = False

    @api.one
    def _full_text_search_update(self):
        # TODO: Remove the context as it doesn't belong in a general purpose module.
        super(product_product, self).with_context(suppress_checks=True)._full_text_search_update()
        self._full_text_search_delete()
        self.write({'fts_dirty': False})
        if self.website_published and self.active:
            self.env['fts.fts'].update_text(self._name, self.id, text=' '.join([self.name, self.default_code, self.ean13]), rank=0)
            self.env['fts.fts'].update_text(self._name, self.id, text=(self.description_sale or '')+' '+ ' '.join([att.name for att in self.attribute_value_ids]), rank=5)


class product_public_category(models.Model):
    _name = 'product.public.category'
    _inherit = ['product.public.category', 'fts.model']

    _fts_fields = ['name']

    @api.one
    def _full_text_search_update(self):
        super(product_public_category, self)._full_text_search_update()
        self.env['fts.fts'].update_text(self._name, self.id, text=self.name, rank=5)
