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


from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

import logging
_logger = logging.getLogger(__name__)


class MemCachedController(http.Controller):

    @http.route([
        '/mcpage/<string:key>',
    ], type='http', auth="public", website=True)
    def memcached_page(self, key='',**post):
        
        page_dict = memcached.MEMCACHED_CLIENT.get(key)
        if page_dict:
            return page_dict.get('page')
        return request.registry['ir.http']._handle_exception(None, 404)
