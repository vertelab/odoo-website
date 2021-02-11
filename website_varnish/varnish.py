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

from odoo.addons.http_routing.models.ir_http import slug

import logging
_logger = logging.getLogger(__name__)

class VarnishController(http.Controller):
    # Set parameters to cache
    relevant_pricelists = []
    relevant_groups = []
    relevant_categories = []

    # ~ def get_user_groups_tag(self):
        # ~ """Get the logged in users' groups, create a tag based upon it, and return it"""
        # ~ groups = request.env.user.groups_id.mapped("id")
        # ~ groups = list(filter(lambda x : x in self.relevant_groups, groups))
        # ~ tag = "_" + ','.join(list(map(str, groups)))
        # ~ return tag

    # ~ def get_pricelist_tag(self):
        # ~ """Get the pricelist and return a tag"""
        # ~ tag = "_" + ','.join(list(map(str, request.env.user.property_product_pricelist.mapped("id"))))
        # ~ return tag

    # ~ def get_category_tag(self):
        # ~ """Get the category and return a tag"""
        # ~ return ""

    # ~ def slug(value):
        # ~ _logger.warning("~ running my slug!!")

    # ~ @slug
    # ~ def slug(self, key='', **post):
        # ~ _logger.warning("~ running my slug!")

#request.env.user_id.group_id.mapped("id")
