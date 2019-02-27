# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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

import logging
_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    # a new field to save vat number temporary. a button action to copy the data from vat_unchecked to vat
    vat_unchecked = fields.Char(string = 'VAT Unchecked')

    @api.one
    def button_insert_vat(self):
        self.vat_subjected = True
        self.vat = self.vat_unchecked

    @api.model
    def remove_inactive_reseller(self):
        partners = self.env['res.partner'].search([('active', '=', False), ('is_company', '=', True), ('name', '=', 'My Company'), ('child_ids', '=', False)])
        issues = self.env['project.issue'].search([('stage_id', '=', self.env.ref('project.project_tt_analysis').id), ('partner_id', 'in', partners.mapped('id'))])
        for i in issues:
            i.unlink()
        for p in partners:
            p.unlink()
