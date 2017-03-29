# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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

from openerp import api, models, fields, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)

class product_facet(models.Model):
    _name = 'product.facet'
    _description = "Product Facet"

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'This facet already exists !')
    ]

    _order = "sequence, name"

    name = fields.Char(string='Name', translate=True, required = True)
    sequence = fields.Integer()
    value_ids = fields.One2many(comodel_name='product.facet.value', string='Facet Values', inverse_name='facet_id')

class product_facet_value(models.Model):
    _name = 'product.facet.value'
    _description = "Product Facet Value"
    _order = 'sequence'

    _sql_constraints = [
        ('value_company_uniq', 'unique (name,facet_id)', 'This facet value already exists !')
    ]

    name = fields.Char(string='Name', translate = True, required = True)
    facet_id = fields.Many2one(comodel_name='product.facet', string='Product Facet', required = True)
    sequence = fields.Integer(string='Sequence')

    @api.multi
    def name_get(self):
        if not self._context.get('show_facet', True):
            return super(product_facet_value, self).name_get()
        res = []
        for value in self:
            res.append([value.id, "%s: %s" % (value.facet_id.name, value.name)])
        return res

class product_facet_line(models.Model):
    _name = 'product.facet.line'
    _description = "Product Facet Lines"

    @api.multi
    def _check_valid_facet(self):
        return self.value_ids <= self.facet_id.value_ids

    _constraints = [
        (_check_valid_facet, 'Error ! You cannot use this facet with the following value.', ['facet_id'])
    ]

    product_tmpl_id = fields.Many2one(comodel_name='product.template', string='Product Templates', required = True)
    facet_id = fields.Many2one(comodel_name='product.facet', string='Product Facet', required = True)
    value_ids = fields.Many2many(comodel_name='product.facet.value', string='Facet Values', required = True)

class product_template(models.Model):
    _inherit = 'product.template'

    facet_line_ids = fields.One2many(comodel_name='product.facet.line', string='Facet Lines', inverse_name='product_tmpl_id')
