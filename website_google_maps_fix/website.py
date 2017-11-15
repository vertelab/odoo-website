# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2017 Vertel AB (<http://vertel.se>).
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
from openerp.http import request
import werkzeug

import logging
_logger = logging.getLogger(__name__)

def urlplus(url, params):
    return werkzeug.Href(url)(params or None)

class Website(models.Model):
    _inherit = 'website'

    google_maps_api_key = fields.Char(string='Google Maps API Key')

class website_config_settings(models.TransientModel):
    _inherit = 'website.config.settings'

    google_maps_api_key = fields.Char(string='Google Maps API Key', related='website_id.google_maps_api_key')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def google_map_img(self, zoom=8, width=298, height=298, marker=None):
        partner = self
        params = {
            'center': '%s, %s %s, %s' % (partner.street or '', partner.city or '', partner.zip or '', partner.country_id and partner.country_id.name_get()[0][1] or ''),
            'size': "%sx%s" % (height, width),
            'zoom': zoom,
            'sensor': 'false',
            'key': request.website.google_maps_api_key,
        }
        if marker:
            mark = ''
            for key in marker:
                mark += '%s:%s|' % (key, marker[key])
            params['markers'] = '%s%s' % (mark, params['center'])
        return urlplus('//maps.googleapis.com/maps/api/staticmap', params)
