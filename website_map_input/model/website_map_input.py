# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2022  https://vertel.se
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _


import logging
# ~ _logger = logging.getLogger(__name__)


class WebsiteMapInput(models.Model):
    _name = 'input.map.website'
    
    @api.model
    def website_map_input(self):
        latitudeInput = fields.Char(string='Latitude input')
        longitudeInput = fields.Char(string='Longitude input')
        radiusInput = fields.Char(string='Radius input')
        locationNameInput = fields.Char(string='Location name input')
