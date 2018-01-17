# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution, third party addon
# Copyright (C) 2018- Vertel AB (<http://vertel.se>).
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
from openerp import http
from openerp.addons.web.http import request
from openerp.addons.website_memcached import memcached

from openerp.addons.website_sale.controllers.main import website_sale

import logging
_logger = logging.getLogger(__name__)

class website_sale(website_sale):

    # '/shop'
    @memcached.route()
    def shop(self, page=0, category=None, search='', **post):
        return super(website_sale, self).shop(page, category, search, **post)

    # '/shop/product/<model("product.template"):product>'
    @memcached.route()
    def product(self, product, category='', search='', **kwargs):
        return super(website_sale, self).product(product, category, search, **kwargs)

    # '/shop/product/comment/<int:product_template_id>'
    @memcached.route()
    def product_comment(self, product_template_id, **post):
        return super(website_sale, self).product_comment(product_template_id, **post)

    # '/shop/pricelist'
    @memcached.route()
    def pricelist(self, promo, **post):
        return super(website_sale, self).pricelist(promo, **post)

    # '/shop/cart'
    @memcached.route()
    def cart(self, **post):
        return super(website_sale, self).cart(**post)

    # '/shop/cart/update'
    @memcached.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **post):
        return super(website_sale, self).cart_update(product_id, add_qty, set_qty, **post)

    # '/shop/checkout'
    @memcached.route()
    def checkout(self, **post):
        return super(website_sale, self).checkout(**post)

    # '/shop/confirm_order'
    @memcached.route()
    def confirm_order(self, **post):
        return super(website_sale, self).confirm_order(**post)

    # '/shop/payment'
    @memcached.route()
    def payment(self, **post):
        return super(website_sale, self).payment(**post)

    # '/shop/payment/validate'
    @memcached.route()
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        return super(website_sale, self).payment_validate(transaction_id, sale_order_id, **post)

    # '/shop/confirmation'
    @memcached.route()
    def payment_confirmation(self, **post):
        return super(website_sale, self).payment_confirmation(**post)

    @http.route(['/website_sale_update_cart'], type='json', auth="public", website=True)
    def website_sale_update_cart(self):
        order = request.website.sale_get_order()
        res = {}
        if order:
            res['amount_total'] = order.amount_total
            res['cart_quantity'] = order.cart_quantity
        return res
