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
from openerp.http import request

import logging
_logger = logging.getLogger(__name__)

class website(models.Model):
    _inherit = 'website'
    
    qty_previous_products = fields.Integer(string='# Previous Products', default=4, help="The number of previous products to display in the webshop.")
    
    @api.multi
    def sale_get_previous_products(self):
        self.ensure_one()
        return self.env['product.template'].browse(request.session.get('previous_product_ids', []))
    
    @api.multi
    def sale_add_previous_product(self, product_id):
        self.ensure_one()
        product_ids = request.session.get('previous_product_ids', [])
        while product_id in product_ids:
            product_ids.remove(product_id)
        product_ids.append(product_id)
        if len(product_ids) > self.qty_previous_products:
            product_ids = product_ids[-self.qty_previous_products:]
        request.session['previous_product_ids'] = product_ids
