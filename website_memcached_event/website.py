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

from openerp.addons.website_event.controllers.main import website_event

import logging
_logger = logging.getLogger(__name__)

class website_event(website_event):

    # '/event'
    @memcached.route()
    def events(self, page=1, **searches):
        return super(website_event, self).events(page, **searches)

    # '/event/<model("event.event"):event>/page/<path:page>'
    @memcached.route()
    def event_page(self, event, page, **post):
        return super(website_event, self).event_page(event, page, **post)

    # '/event/<model("event.event"):event>/register'
    @memcached.route()
    def event_register(self, event, **post):
        return super(website_event, self).event_register(event, **post)

    # '/event/get_country_event_list'
    @memcached.route()
    def get_country_events(self, **post):
        return super(website_event, self).get_country_events(**post)
