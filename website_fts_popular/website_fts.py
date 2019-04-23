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

class FtsModel(models.Model):
    _inherit = 'fts.model'

    #~ fts_nbr_searches = fields.Integer(string="#Searches",index=True)
    #~ fts_last_search = fields.Datetime(string="Last search")
    #~ @api.one
    #~ @api.depends('fts_last_search','fts_nbr_searches')
    #~ def _fts_last_week(self):
        #~ self.fts_last_week = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.fts_last_search)).days < 7 if self.fts_last_search else None
        #~ self.fts_last_month = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.fts_last_search)).days < 31 if self.fts_last_search else None
        #~ self.fts_last_quarter = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.fts_last_search)).days < 92 if self.fts_last_search else None
        #~ self.fts_last_halfyear = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.fts_last_search)).days < 182 if self.fts_last_search else None
        #~ self.fts_last_year = (fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(self.fts_last_search)).days < 365 if self.fts_last_search else None
    #~ fts_last_week = fields.Boolean(string="Last week",compute="_fts_last_week",store=True)
    #~ fts_last_month = fields.Boolean(string="Last month",compute="_fts_last_week",store=True)
    #~ fts_last_quarter = fields.Boolean(string="Last quarter",compute="_fts_last_week",store=True)
    #~ fts_last_halfyear = fields.Boolean(string="Last half year",compute="_fts_last_week",store=True)
    #~ fts_last_year = fields.Boolean(string="Last year",compute="_fts_last_week",store=True)

    # TODO: Check why this method breaks te test search.
    #~ @api.model
    #~ def fts_term_search(self, query, models=None, limit=25, domain=None, offset=0):
        #~ res = super(FtsModel, self).fts_term_search(query, models=models, limit=limit, domain=domain, offset=offset)
        #~ _logger.warn(res)
        #~ return res

class fts_popular(models.Model):
    _name = 'fts.popular'
    _order = "sequence,name"

    name = fields.Char(string="Word")
    sequence = fields.Integer()
    fts_id = fields.Many2one(comodel_name="fts.fts", ondelete='cascade')
    fts_nbr_searches = fields.Integer(related="fts_id.fts_nbr_searches")
    fts_last_search = fields.Datetime(related="fts_id.fts_last_search")
    count = fields.Integer(related="fts_id.count")
    rank = fields.Integer(related="fts_id.rank")
    
    


