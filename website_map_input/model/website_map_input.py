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

from odoo import models, fields, api, exceptions, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate

import logging
# ~ _logger = logging.getLogger(__name__)


class MapInput(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'website.seo.metadata', 'website.published.multi.mixin']

    public_info = fields.Char(string='Public Info')

    def _compute_website_url(self):
        super(HrEmployee, self)._compute_website_url()
        for employee in self:
            employee.website_url = '/aboutus'

    def sort_familyname(self,rec):
        return rec.sorted(lambda r: r.name.split(' ')[1])

class HrEmployeePublic(models.Model):
    _name = 'hr.employee.public'
    _inherit = ['hr.employee.public', 'website.seo.metadata', 'website.published.multi.mixin']

    public_info = fields.Char(string='Public Info')
