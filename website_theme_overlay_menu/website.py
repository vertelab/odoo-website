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
from openerp import http
from openerp.http import request
from datetime import datetime
from lxml import html
import werkzeug

from openerp.addons.website.models.website import slug

class website(models.Model):
    _inherit = "website"
    
    def get_mega_menu_categories(self):
        children = self.env['product.public.category'].search([('parent_id', '=', None), ('website_published', '=', True)], order='sequence asc')
        # _logger.warn('sandra %s' % children.mapped('name'))

        return children 
        
            # self.env.ref('__export__.product_public_category_4'),
            # self.env.ref('__export__.product_public_category_3'),
            # self.env.ref('__export__.product_public_category_2'),
            # self.env.ref('__export__.product_public_category_5'),
            # self.env.ref('__export__.product_public_category_6'),


        
        
    def make_categ_link(self, value):
        return '/webshop/category/%s' %slug(value)
        