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
from odoo import models, fields, api, _

class website_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    memcached_db = fields.Char(string='Memcached Databases', default='[("localhost", 11211)]', help="A list of memcached databases  [('server',<port>),...]")

    @api.model
    def get_default_memcached_db(self, fields):
        return {'memcached_db': self.env['ir.config_parameter'].get_param('website_memcached.memcached_db') or '("localhost", 11211)'}

    def set_memcached_db(self):
        self.ensure_one()
        self.env['ir.config_parameter'].set_param('website_memcached.memcached_db', self.memcached_db)
