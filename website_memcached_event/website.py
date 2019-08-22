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
from openerp import models, fields, api, _
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website_event.controllers.main import website_event

import logging
_logger = logging.getLogger(__name__)


class Event(models.Model):
    _inherit = 'event.event'
    
    memcached_time = fields.Datetime(string='Memcached Timestamp', default=lambda *args, **kwargs: fields.Datetime.now(), help="Last modification relevant to memcached.")

class event_registration(models.Model):
    _inherit = 'event.registration'

    @api.one
    def do_draft(self):
        super(event_registration, self).do_draft()
        self.event_id.memcached_time = fields.Datetime.now()

    @api.one
    def confirm_registration(self):
        super(event_registration, self).confirm_registration()
        self.event_id.memcached_time = fields.Datetime.now()

    @api.one
    def registration_open(self):
        super(event_registration, self).registration_open()
        self.event_id.memcached_time = fields.Datetime.now()

    @api.one
    def button_reg_close(self):
        super(event_registration, self).button_reg_close()
        self.event_id.memcached_time = fields.Datetime.now()

    @api.one
    def button_reg_cancel(self):
        super(event_registration, self).button_reg_cancel()
        self.event_id.memcached_time = fields.Datetime.now()

class Website(models.Model):
    _inherit = 'website'

    def get_kw_event(self, kw):
        return kw['event'].name if kw.get('event', None) else ''

class website_event(website_event):

    # '/event'
    @memcached.route(key=lambda kw: '{db}/event{employee}{logged_in}{publisher}{designer}{lang}%s' % (request.env['event.event'].search_read([('website_published', '=', True), ('memcached_time', '!=', False)], ['memcached_time'], limit=1, order='memcached_time desc' ) or {'memcached_time': ''} )['memcached_time'])
    def events(self, page=1, **searches):
        return super(website_event, self).events(page, **searches)

    # '/event/<model("event.event"):event>/page/<path:page>'
    @memcached.route(
        flush_type=lambda kw: 'event %s' %request.website.get_kw_event(kw),
        key=lambda kw: '{db}/event/%s/page/page{employee}{logged_in}{publisher}{designer}{lang}%s' % (kw.get('event') and (kw['event'].id, kw['event'].memcached_time or '') or ('', '')))
    def event_page(self, event, page, **post):
        return super(website_event, self).event_page(event, page, **post)

    # '/event/<model("event.event"):event>/register'
    @memcached.route(
        flush_type=lambda kw: 'event register %s' %request.website.get_kw_event(kw),
        key=lambda kw: '{db}/event/%s/register{employee}{logged_in}{publisher}{designer}{lang}%s' % (kw.get('event') and (kw['event'].id, kw['event'].memcached_time or '') or ('', '')))
    def event_register(self, event, **post):
        return super(website_event, self).event_register(event, **post)

    # '/event/get_country_event_list'
    @memcached.route(
        key=lambda kw: '{db}/event/get_country_event_list{employee}{logged_in}{publisher}{designer}{lang}%s' % (request.env['event.event'].search_read([('website_published', '=', True), ('memcached_time', '!=', False)], ['memcached_time'], limit=1, order='memcached_time desc' ) or {'memcached_time': ''} )['memcached_time'])
    def get_country_events(self, **post):
        return super(website_event, self).get_country_events(**post)
