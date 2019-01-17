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

import openerp
from openerp import models, fields, api, _
import traceback
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

class WebsiteErrorLog(models.Model):
    _name = 'website.error.log'
    _order = 'time desc'

    name = fields.Char(string='Path', required=True)
    website_id = fields.Many2one(comodel_name='website', string='Website')
    code = fields.Integer(string='Code')
    exception_message = fields.Char(string='Error Message')
    traceback = fields.Text(string='Traceback')
    qweb_message = fields.Text(string='Qweb Message')
    qweb_expression = fields.Text(string='Qweb Expression')
    qweb_node = fields.Text(string='Qweb Node')
    view_id = fields.Many2one(comodel_name='ir.ui.view', string='Qweb Template')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    time = fields.Datetime(string='Time', required=True)
    age = fields.Float(string='Age', compute='get_age', search='search_age', help="Age in minutes")

    @api.one
    def get_age(self):
        self.age = fields.Datetime.to_string(fields.Datetime.from_string(fields.Datetime.now()) - fields.Datetime.from_string(self.time))

    @api.model
    def search_age(self, operator, value):
        value = fields.Datetime.to_string(fields.Datetime.from_string(fields.Datetime.now()) - timedelta(0, int(value * 60)))
        if operator == '>':
            operator = '<'
        elif operator == '>=':
            operator = '<='
        elif operator == '<':
            operator = '>'
        elif operator == '<=':
            operator = '>='
        return [('time', operator, value)]

    @api.model
    def log_error(self, request, response, code, values):
        values = values or {}
        # (V)odoo magic!
        # The current cursor is/will get rolled back. Create a new one to be able to save the log.
        with openerp.registry(self.env.cr.dbname).cursor() as new_cr:
            with api.Environment.manage():
                new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                log_obj = new_env['website.error.log'].sudo()
                try:
                    website = getattr(request, 'website_enabled', False) and request.website
                    log_obj.create(log_obj.get_error_values(request, response, code, values, website))
                except Exception as e:
                    _logger.error('Error when logging website error:\n\n%s' % traceback.format_exc(e))
                new_env.cr.commit()

    @api.model
    def get_error_values(self, request, response, code, values, website):
        exception = values.get('exception')
        if not exception and isinstance(response, Exception):
            exception = response
        tb = values.get('traceback') or (exception and traceback.format_exc(exception)) or None
        qweb_exception = values.get('qweb_exception')
        qweb = qweb_exception and getattr(qweb_exception, 'qweb', {}) or {}
        template_id = qweb.get('template')
        if template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id(template_id, False)
        return {
            'name': request.httprequest.path,
            'website_id': website and website.id or False,
            'code': code,
            'exception_message': exception and exception.message,
            'traceback': tb,
            'view_id': template_id,
            'qweb_message': qweb.get('message'),
            'qweb_expression': qweb.get('expression'),
            'qweb_node': qweb_exception and qweb_exception.pretty_xml(),
            'user_id': request.env.uid,
            'time': fields.Datetime.now(),
        }
