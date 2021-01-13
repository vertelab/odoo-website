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

import logging
_logger = logging.getLogger(__name__)

class VarnishController(http.Controller):
    def get_user_groups_tag(self):
        """Get the logged in users' groups, create a tag based upon it, and return it"""
        return ""

    def get_pricelist_tag(self):
        """Get the pricelist and return a tag"""
        return ""

    def get_category_tag(self):
        """Get the category and return a tag"""
        return ""

    @http.route(['/varnishurl',], type='http', auth="user", website=True)
    def varnish_page(self, key='', **post):
        _logger.warning("~ running varnish_page!")
        _logger.warning("~ TODO:")
        _logger.warning("~ * add user tag to URL?")
        _logger.warning("~ * add pricelist tag to URL?")
        _logger.warning("~ * add product tag to URL?")
