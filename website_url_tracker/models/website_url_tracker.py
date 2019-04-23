# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2019- Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, tools, _
import logging
_logger = logging.getLogger(__name__)


class website_url_tracker(models.Model):
    _name = 'website.url.tracker'

    timestamp = fields.Datetime(string='Time Stamp')
    user_id = fields.Many2one(comodel_name='res.users', string='Visitor')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    referer_base = fields.Char(string='Referer Base')
    referer = fields.Char(string='Referer')


class website_url_tracker_analysis(models.Model):
    _name = 'website.url.tracker.analysis'
    _description = 'Website URL Tracker Analysis'
    _auto = False
    _rec_name = 'timestamp'
    _order = 'timestamp desc'

    timestamp = fields.Datetime(string='Time Stamp', readonly=True)
    user_id = fields.Many2one(comodel_name='res.users', string='Visitor', readonly=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', readonly=True)
    referer_base = fields.Char(string='Referer Base', readonly=True)
    referer = fields.Char(string='Referer', readonly=True)

    def _select(self):
        select_str = """
             SELECT min(wut.id) as id,
                    wut.id as wut_id,
                    wut.partner_id as partner_id,
                    wut.user_id as user_id,
                    wut.timestamp as timestamp,
                    wut.referer_base as referer_base,
                    wut.referer as referer
        """
        return select_str

    def _from(self):
        from_str = """
                website_url_tracker wut
                    left join res_partner rp on (wut.partner_id = rp.id)
                    left join res_users ru on (wut.user_id = ru.id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                    wut.partner_id,
                    wut.user_id,
                    wut.timestamp,
                    wut.referer_base,
                    wut.referer,
                    wut.id
        """
        return group_by_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        query = """CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by())
        cr.execute(query)
