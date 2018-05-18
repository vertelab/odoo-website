# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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
from odoo import http
from odoo.http import request
from odoo.addons.website_memcached import memcached

from odoo.addons.website_sale.controllers.main import WebsiteSale

import logging
_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

    # '/shop'
    @memcached.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        return super(WebsiteSale, self).shop(page, category, search, **post)

    # '/shop/product/<model("product.template"):product>'
    @memcached.route()
    def product(self, product, category='', search='', **kwargs):
        return super(WebsiteSale, self).product(product, category, search, **kwargs)
