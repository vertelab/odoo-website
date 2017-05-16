# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models, fields, api, _
import json
from openerp.addons.web import http
from openerp.http import request
import logging
_logger = logging.getLogger(__name__)

class ir_ui_view(models.Model):
    _inherit = 'ir.ui.view'

    website_published = fields.Boolean()
    @api.one
    def _can_view(self):
        page = self.env['ir.ui.view'].sudo().browse(self.id)
        if self._uid in self.sudo().env.ref('base.group_website_publisher').mapped('users.id'):
            self.can_view = True
        else:
            self.can_view = (self._uid in page.groups_id.mapped('users.id') or page.groups_id.mapped('users.id') == []) and self.website_published
    can_view = fields.Boolean(compute='_can_view')

class res_groups(models.Model):
    _inherit = 'res.groups'

    @api.one
    def _external_id(self):
        self.external_id = self.env['ir.model.data'].search([('model', '=', self._name), ('res_id', '=', self.id)]).mapped('complete_name')[0]
    external_id = fields.Char(compute='_external_id')

class website_page_groups(http.Controller):

    @http.route(['/website_page_groups/set_groups'], type='json', auth="public", website=True)
    def set_groups(self, groups, page_id, **kwarg):
        page = request.env['ir.ui.view'].browse(int(page_id))
        groups_list = []
        if groups != '':
            for gid in groups.split(','):
                groups_list.append(request.env.ref(str(gid)).id)
        if groups_list == []:
            page.groups_id = [(5, 0, 0)]
        else:
            for group in groups_list:
                page.groups_id = [(4, group, 0)]
        return groups
