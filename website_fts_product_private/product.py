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
    _inherit = 'product.template'

    @api.one
    def _full_text_search_update(self):
        self._full_text_search_delete()
        self.write({'fts_dirty': False})
        if self.website_published and self.active:
            self.env['fts.fts'].update_text(self._name, self.id, text=self.name, rank=0, groups=self.access_group_ids)
            if self.description_sale:
                self.env['fts.fts'].update_text(self._name, self.id, text=self.description_sale, rank=5, groups=self.access_group_ids)

class product_product(models.Model):
    _inherit = 'product.product'

    @api.one
    def _full_text_search_update(self):
        self._full_text_search_delete()
        self.write({'fts_dirty': False})
        if self.website_published and self.active:
            self.env['fts.fts'].update_text(self._name,self.id,text=' '.join([self.name, self.default_code, self.ean13]),rank=0, groups=self.access_group_ids)
            self.env['fts.fts'].update_text(self._name,self.id,text=(self.description_sale or '')+' '+ ' '.join([att.name for att in self.attribute_value_ids]),rank=5, groups=self.access_group_ids)
