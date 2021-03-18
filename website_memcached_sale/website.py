
from odoo import http
from odoo.http import request
from odoo.service import common
from odoo.addons.website_memcached import memcached

from odoo.addons.website_sale.controllers.main import WebsiteSaleForm
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_form.controllers.main import WebsiteForm


import logging
_logger = logging.getLogger(__name__)


# ~ class WebsiteSaleForm(WebsiteForm):

    #'/shop'
    # ~ @memcached.route(
        #key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        # ~ flush_type=lambda kw: 'webshop',
        # ~ no_cache=True,
        # ~ cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        # ~ max_age=31536000, # Webbläsare
        # ~ s_maxage=600)     # Varnish
    # ~ def shop(self, page=0, category=None, search='', **post):
        # ~ return super(WebsiteSale, self).shop(page, category, search, **post)


    #@http.route('/website_form/shop.sale.order', type='http', auth="public", methods=['POST'], website=True)
    # ~ @memcached.route(
        #key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        # ~ flush_type=lambda kw: 'webshop',
        # ~ no_cache=True,
        # ~ cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        # ~ max_age=31536000, # Webbläsare
        # ~ s_maxage=600)     # Varnish
    # ~ def shop(self, page=0, category=None, search='', **post):
        # ~ return super(WebsiteSaleForm, self).website_form_saleorder(kwargs)


class WebsiteSale(WebsiteSale):

    # ~ @http.route([
        # ~ '''/shop''',
        # ~ '''/shop/page/<int:page>''',
        # ~ '''/shop/category/<model("product.public.category"):category>''',
        # ~ '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    # ~ ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        return super(WebsiteSale, self).shop(page,category, search, ppg, post)

    # ~ @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def product(self, product, category='', search='', **kwargs):
        return super(WebsiteSale, self).product(product, category, search,kwargs)




    @http.route(['/shop/change_pricelist/<model("product.pricelist"):pl_id>'], type='http', auth="public", website=True, sitemap=False)
    def pricelist_change(self, pl_id, **post):
        if (pl_id.selectable or pl_id == request.env.user.partner_id.property_product_pricelist) \
                and request.website.is_pricelist_available(pl_id.id):
            request.session['website_sale_current_pl'] = pl_id.id
            request.website.sale_get_order(force_pricelist=pl_id.id)
        return request.redirect(request.httprequest.referrer or '/shop')

    # ~ @http.route(['/shop/pricelist'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def pricelist(self, promo, **post):
        return super(WebsiteSale, self).pricelist(promo, post)

    # ~ @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def cart(self, access_token=None, revive='', **post):
        return super(WebsiteSale, self).cart(access_token, revive, post)

    # ~ @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        return super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty, kw)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template("website_sale.short_cart_summary", {
            'website_sale_order': order,
        })
        return value

    @http.route('/shop/save_shop_layout_mode', type='json', auth='public', website=True)
    def save_shop_layout_mode(self, layout_mode):
        assert layout_mode in ('grid', 'list'), "Invalid shop layout mode"
        request.session['website_sale_shop_layout_mode'] = layout_mode


    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                            (not order.only_services and (mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'country_states': country.get_website_sale_states(mode=mode[1]),
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        return request.render("website_sale.address", render_values)

    # ~ @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def checkout(self, **post):
        return super(WebsiteSale, self).checkout(post)

    # ~ @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def confirm_order(self, **post):
        return super(WebsiteSale, self).confirm_order(post)
    # ------------------------------------------------------
    # Extra step
    # ------------------------------------------------------
    @http.route(['/shop/extra_info'], type='http', auth="public", website=True, sitemap=False)
    def extra_info(self, **post):
        # Check that this option is activated
        extra_step = request.website.viewref('website_sale.extra_info_option')
        if not extra_step.active:
            return request.redirect("/shop/payment")

        # check that cart is valid
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        # if form posted
        if 'post_values' in post:
            values = {}
            for field_name, field_value in post.items():
                if field_name in request.env['sale.order']._fields and field_name.startswith('x_'):
                    values[field_name] = field_value
            if values:
                order.write(values)
            return request.redirect("/shop/payment")

        values = {
            'website_sale_order': order,
            'post': post,
            'escape': lambda x: x.replace("'", r"\'"),
            'partner': order.partner_id.id,
            'order': order,
        }

        return request.render("website_sale.extra_info", values)

    # ------------------------------------------------------
    # Payment
    # ------------------------------------------------------

    def _get_shop_payment_values(self, order, **kwargs):
        values = dict(
            website_sale_order=order,
            errors=[],
            partner=order.partner_id.id,
            order=order,
            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
            return_url= '/shop/payment/validate',
            bootstrap_formatting= True
        )

        domain = expression.AND([
            ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order.company_id.id)],
            ['|', ('website_id', '=', False), ('website_id', '=', request.website.id)],
            ['|', ('country_ids', '=', False), ('country_ids', 'in', [order.partner_id.country_id.id])]
        ])
        acquirers = request.env['payment.acquirer'].search(domain)

        values['access_token'] = order.access_token
        values['acquirers'] = [acq for acq in acquirers if (acq.payment_flow == 'form' and acq.view_template_id) or
                                    (acq.payment_flow == 's2s' and acq.registration_view_template_id)]
        values['tokens'] = request.env['payment.token'].search([
            ('acquirer_id', 'in', acquirers.ids),
            ('partner_id', 'child_of', order.partner_id.commercial_partner_id.id)])

        if order:
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order.amount_total, order.currency_id, order.partner_id.country_id.id)
        return values

    # ~ @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def payment(self, **post):
        return(WebsiteSale, self).payment(post)
        
    @http.route(['/shop/payment/transaction/',
        '/shop/payment/transaction/<int:so_id>',
        '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()

        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.render_sale_button(order)

    @http.route('/shop/payment/token', type='http', auth='public', website=True, sitemap=False)
    def payment_token(self, pm_id=None, **kwargs):
        """ Method that handles payment using saved tokens

        :param int pm_id: id of the payment.token that we want to use to pay.
        """
        order = request.website.sale_get_order()
        # do not crash if the user has already paid and try to pay again
        if not order:
            return request.redirect('/shop/?error=no_order')

        assert order.partner_id.id != request.website.partner_id.id

        try:
            pm_id = int(pm_id)
        except ValueError:
            return request.redirect('/shop/?error=invalid_token_id')

        # We retrieve the token the user want to use to pay
        if not request.env['payment.token'].sudo().search_count([('id', '=', pm_id)]):
            return request.redirect('/shop/?error=token_not_found')

        # Create transaction
        vals = {'payment_token_id': pm_id, 'return_url': '/shop/payment/validate'}

        tx = order._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)
        return request.redirect('/payment/process')

    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def payment_get_status(self, sale_order_id, **post):
        order = request.env['sale.order'].sudo().browse(sale_order_id).exists()
        if order.id != request.session.get('sale_last_order_id'):
            # either something went wrong or the session is unbound
            # prevent recalling every 3rd of a second in the JS widget
            return {}

        return {
            'recall': order.get_portal_last_transaction().state == 'pending',
            'message': request.env['ir.ui.view']._render_template("website_sale.payment_confirmation_status", {
                'order': order
            })
        }

    # ~ @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        return super(WebsiteSale, self).payment_validate(transaction_id, sole_order_id, post)
        
    @http.route(['/shop/terms'], type='http', auth="public", website=True, sitemap=True)
    def terms(self, **kw):
        return request.render("website_sale.terms")

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop')

    @http.route(['/shop/print'], type='http', auth="public", website=True, sitemap=False)
    def print_saleorder(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            pdf, _ = request.env.ref('sale.action_report_saleorder').sudo()._render_qweb_pdf([sale_order_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop')

    @http.route(['/shop/tracking_last_order'], type='json', auth="public")
    def tracking_cart(self, **post):
        """ return data about order in JSON needed for google analytics"""
        ret = {}
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            ret = self.order_2_return_dict(order)
        return ret

    # ------------------------------------------------------
    # Edit
    # ------------------------------------------------------

    @http.route(['/shop/add_product'], type='json', auth="user", methods=['POST'], website=True)
    def add_product(self, name=None, category=None, **post):
        product = request.env['product.product'].create({
            'name': name or _("New Product"),
            'public_categ_ids': category,
            'website_id': request.website.id,
        })
        return "%s?enable_editor=1" % product.product_tmpl_id.website_url

    @http.route(['/shop/change_sequence'], type='json', auth='user')
    def change_sequence(self, id, sequence):
        product_tmpl = request.env['product.template'].browse(id)
        if sequence == "top":
            product_tmpl.set_sequence_top()
        elif sequence == "bottom":
            product_tmpl.set_sequence_bottom()
        elif sequence == "up":
            product_tmpl.set_sequence_up()
        elif sequence == "down":
            product_tmpl.set_sequence_down()

    @http.route(['/shop/change_size'], type='json', auth='user')
    def change_size(self, id, x, y):
        product = request.env['product.template'].browse(id)
        return product.write({'website_size_x': x, 'website_size_y': y})

    @http.route(['/shop/change_ppg'], type='json', auth='user')
    def change_ppg(self, ppg):
        request.env['website'].get_current_website().shop_ppg = ppg

    @http.route(['/shop/change_ppr'], type='json', auth='user')
    def change_ppr(self, ppr):
        request.env['website'].get_current_website().shop_ppr = ppr

    def order_lines_2_google_api(self, order_lines):
        """ Transforms a list of order lines into a dict for google analytics """
        ret = []
        for line in order_lines:
            product = line.product_id
            ret.append({
                'id': line.order_id.id,
                'sku': product.barcode or product.id,
                'name': product.name or '-',
                'category': product.categ_id.name or '-',
                'price': line.price_unit,
                'quantity': line.product_uom_qty,
            })
        return ret

    def order_2_return_dict(self, order):
        """ Returns the tracking_cart dict of the order for Google analytics basically defined to be inherited """
        return {
            'transaction': {
                'id': order.id,
                'affiliation': order.company_id.name,
                'revenue': order.amount_total,
                'tax': order.amount_tax,
                'currency': order.currency_id.name
            },
            'lines': self.order_lines_2_google_api(order.order_line)
        }

    @http.route(['/shop/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def country_infos(self, country, mode, **kw):
        return dict(
            fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in country.get_website_sale_states(mode=mode)],
            phone_code=country.phone_code,
            zip_required=country.zip_required,
            state_required=country.state_required,
        )

    # --------------------------------------------------------------------------
    # Products Search Bar
    # --------------------------------------------------------------------------

    @http.route('/shop/products/autocomplete', type='json', auth='public', website=True)
    def products_autocomplete(self, term, options={}, **kwargs):
        """
        Returns list of products according to the term and product options

        Params:
            term (str): search term written by the user
            options (dict)
                - 'limit' (int), default to 5: number of products to consider
                - 'display_description' (bool), default to True
                - 'display_price' (bool), default to True
                - 'order' (str)
                - 'max_nb_chars' (int): max number of characters for the
                                        description if returned

        Returns:
            dict (or False if no result)
                - 'products' (list): products (only their needed field values)
                        note: the prices will be strings properly formatted and
                        already containing the currency
                - 'products_count' (int): the number of products in the database
                        that matched the search query
        """
        ProductTemplate = request.env['product.template']

        display_description = options.get('display_description', True)
        display_price = options.get('display_price', True)
        order = self._get_search_order(options)
        max_nb_chars = options.get('max_nb_chars', 999)

        category = options.get('category')
        attrib_values = options.get('attrib_values')

        domain = self._get_search_domain(term, category, attrib_values, display_description)
        products = ProductTemplate.search(
            domain,
            limit=min(20, options.get('limit', 5)),
            order=order
        )

        fields = ['id', 'name', 'website_url']
        if display_description:
            fields.append('description_sale')

        res = {
            'products': products.read(fields),
            'products_count': ProductTemplate.search_count(domain),
        }

        if display_description:
            for res_product in res['products']:
                desc = res_product['description_sale']
                if desc and len(desc) > max_nb_chars:
                    res_product['description_sale'] = "%s..." % desc[:(max_nb_chars - 3)]

        if display_price:
            FieldMonetary = request.env['ir.qweb.field.monetary']
            monetary_options = {
                'display_currency': request.website.get_current_pricelist().currency_id,
            }
            for res_product, product in zip(res['products'], products):
                combination_info = product._get_combination_info(only_template=True)
                res_product.update(combination_info)
                res_product['list_price'] = FieldMonetary.value_to_html(res_product['list_price'], monetary_options)
                res_product['price'] = FieldMonetary.value_to_html(res_product['price'], monetary_options)

        return res

    # --------------------------------------------------------------------------
    # Products Recently Viewed
    # --------------------------------------------------------------------------
    @http.route('/shop/products/recently_viewed', type='json', auth='public', website=True)
    def products_recently_viewed(self, **kwargs):
        return self._get_products_recently_viewed()

    def _get_products_recently_viewed(self):
        """
        Returns list of recently viewed products according to current user
        """
        max_number_of_product_for_carousel = 12
        visitor = request.env['website.visitor']._get_visitor_from_request()
        if visitor:
            excluded_products = request.website.sale_get_order().mapped('order_line.product_id.id')
            products = request.env['website.track'].sudo().read_group(
                [('visitor_id', '=', visitor.id), ('product_id', '!=', False), ('product_id.website_published', '=', True), ('product_id', 'not in', excluded_products)],
                ['product_id', 'visit_datetime:max'], ['product_id'], limit=max_number_of_product_for_carousel, orderby='visit_datetime DESC')
            products_ids = [product['product_id'][0] for product in products]
            if products_ids:
                viewed_products = request.env['product.product'].with_context(display_default_code=False).browse(products_ids)

                FieldMonetary = request.env['ir.qweb.field.monetary']
                monetary_options = {
                    'display_currency': request.website.get_current_pricelist().currency_id,
                }
                rating = request.website.viewref('website_sale.product_comment').active
                res = {'products': []}
                for product in viewed_products:
                    combination_info = product._get_combination_info_variant()
                    res_product = product.read(['id', 'name', 'website_url'])[0]
                    res_product.update(combination_info)
                    res_product['price'] = FieldMonetary.value_to_html(res_product['price'], monetary_options)
                    if rating:
                        res_product['rating'] = request.env["ir.ui.view"]._render_template('portal_rating.rating_widget_stars_static', values={
                            'rating_avg': product.rating_avg,
                            'rating_count': product.rating_count,
                        })
                    res['products'].append(res_product)

                return res
        return {}

    @http.route('/shop/products/recently_viewed_update', type='json', auth='public', website=True)
    def products_recently_viewed_update(self, product_id, **kwargs):
        res = {}
        visitor_sudo = request.env['website.visitor']._get_visitor_from_request(force_create=True)
        if visitor_sudo:
            if request.httprequest.cookies.get('visitor_uuid', '') != visitor_sudo.access_token:
                res['visitor_uuid'] = visitor_sudo.access_token
            visitor_sudo._add_viewed_product(product_id)
        return res

    @http.route('/shop/products/recently_viewed_delete', type='json', auth='public', website=True)
    def products_recently_viewed_delete(self, product_id, **kwargs):
        visitor_sudo = request.env['website.visitor']._get_visitor_from_request()
        if visitor_sudo:
            request.env['website.track'].sudo().search([('visitor_id', '=', visitor_sudo.id), ('product_id', '=', product_id)]).unlink()
        return self._get_products_recently_viewed()

    # --------------------------------------------------------------------------
    # Website Snippet Filters
    # --------------------------------------------------------------------------

    @http.route('/website_sale/snippet/options_filters', type='json', auth='user', website=True)
    def get_dynamic_snippet_filters(self):
        domain = expression.AND([
            request.website.website_domain(),
            ['|', ('filter_id.model_id', '=', 'product.product'), ('action_server_id.model_id.model', '=', 'product.product')]
        ])
        filters = request.env['website.snippet.filter'].sudo().search_read(
            domain, ['id']
        )
        return filters









#-------------------------------------------
# ~ class website_sale(website_sale):

    # ~ # '/shop'
    # ~ @memcached.route()
    # ~ def shop(self, page=0, category=None, search='', **post):
        # ~ return super(website_sale, self).shop(page, category, search, **post)

    # ~ # '/shop/product/<model("product.template"):product>'
    # ~ @memcached.route()
    # ~ def product(self, product, category='', search='', **kwargs):
        # ~ return super(website_sale, self).product(product, category, search, **kwargs)

    # ~ # '/shop/product/comment/<int:product_template_id>'
    # ~ @memcached.route()
    # ~ def product_comment(self, product_template_id, **post):
        # ~ return super(website_sale, self).product_comment(product_template_id, **post)

    # ~ # '/shop/pricelist'
    # ~ @memcached.route()
    # ~ def pricelist(self, promo, **post):
        # ~ return super(website_sale, self).pricelist(promo, **post)

    # ~ # '/shop/cart'
    # ~ @memcached.route()
    # ~ def cart(self, **post):
        # ~ return super(website_sale, self).cart(**post)

    # ~ # '/shop/cart/update'
    # ~ @memcached.route()
    # ~ def cart_update(self, product_id, add_qty=1, set_qty=0, **post):
        # ~ return super(website_sale, self).cart_update(product_id, add_qty, set_qty, **post)

    # ~ # '/shop/checkout'
    # ~ @memcached.route()
    # ~ def checkout(self, **post):
        # ~ return super(website_sale, self).checkout(**post)

    # ~ # '/shop/confirm_order'
    # ~ @memcached.route()
    # ~ def confirm_order(self, **post):
        # ~ return super(website_sale, self).confirm_order(**post)

    # ~ # '/shop/payment'
    # ~ @memcached.route()
    # ~ def payment(self, **post):
        # ~ return super(website_sale, self).payment(**post)

    # ~ # '/shop/payment/validate'
    # ~ @memcached.route()
    # ~ def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        # ~ return super(website_sale, self).payment_validate(transaction_id, sale_order_id, **post)

    # ~ # '/shop/confirmation'
    # ~ @memcached.route()
    # ~ def payment_confirmation(self, **post):
        # ~ return super(website_sale, self).payment_confirmation(**post)

    # ~ @http.route(['/website_sale_update_cart'], type='json', auth="public", website=True)
    # ~ def website_sale_update_cart(self):
        # ~ order = request.website.sale_get_order()
        # ~ res = {'amount_total': '0.00', 'cart_quantity': '0'}
        # ~ if order:
            # ~ res['amount_total'] = "%.2f" %order.amount_total
            # ~ res['cart_quantity'] = order.cart_quantity
        # ~ if request.env.lang == 'sv_SE':
            # ~ res['amount_total'] = res['amount_total'].replace('.', ',')
        # ~ return res

