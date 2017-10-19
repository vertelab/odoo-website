# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2017 Vertel AB (<http://vertel.se>).
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
from openerp.http import request
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class fts_fts(models.Model):
    _inherit = 'fts.fts'

    nbr_searches = fields.Integer(string="#Searches",index=True)
    last_search = fields.Datetime(string="Last search")
    @api.one
    @api.depends('last_search','nbr_searches')
    def _last_week(self):
        self.last_week = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.last_search)).days < 7 if self.last_search else None
        self.last_month = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.last_search)).days < 31 if self.last_search else None
        self.last_quarter = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.last_search)).days < 92 if self.last_search else None
        self.last_halfyear = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.last_search)).days < 182 if self.last_search else None
        self.last_year = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.last_search)).days < 365 if self.last_search else None
    last_week = fields.Boolean(string="Last week",compute="_last_week",store=True)
    last_month = fields.Boolean(string="Last month",compute="_last_week",store=True)
    last_quarter = fields.Boolean(string="Last quarter",compute="_last_week",store=True)
    last_halfyear = fields.Boolean(string="Last half year",compute="_last_week",store=True)
    last_year = fields.Boolean(string="Last year",compute="_last_week",store=True)

    @api.model
    def term_search(self, word_list=[], facet=None, res_model=None, limit=5, offset=0):
        res = super(fts_fts, self).term_search(word_list, facet, res_model, limit, offset)
        for term in res['terms']:
            term.write({'nbr_searches': term.nbr_searches + 1, 'last_search': fields.Datetime.now()})
        return res

class fts_popular(models.Model):
    _name = 'fts.popular'
    _order = "sequence,name"

    name = fields.Char(string="Word")
    sequence = fields.Integer()
    fts_id = fields.Many2one(comodel_name="fts.fts", ondelete='cascade')
    nbr_searches = fields.Integer(related="fts_id.nbr_searches")
    last_search = fields.Datetime(related="fts_id.last_search")
    count = fields.Integer(related="fts_id.count")
    rank = fields.Integer(related="fts_id.rank")



