
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
        return super(WebsiteSale, self).shop(page,category, search, ppg, **post)
        #return super(WebsiteSale, self).shop()

    # ~ @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def product(self, product, category='', search='', **kwargs):
        return super(WebsiteSale, self).product(product, category, search,**kwargs)




    # ~ @http.route(['/shop/change_pricelist/<model("product.pricelist"):pl_id>'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def pricelist_change(self, pl_id, **post):
        return super(WebsiteSale, self).pricelist_change(pl_id, **post)

    # ~ @http.route(['/shop/pricelist'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def pricelist(self, promo, **post):
        return super(WebsiteSale, self).pricelist(promo, **post)

    # ~ @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def cart(self, access_token=None, revive='', **post):
        return super(WebsiteSale, self).cart(access_token, revive, **post)

    # ~ @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        return super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty, **kw)

    # ~ @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        return super(WebsiteSale, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)

    # ~ @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def checkout(self, **post):
        return super(WebsiteSale, self).checkout(**post)

    # ~ @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def confirm_order(self, **post):
        return super(WebsiteSale, self).confirm_order(**post)
    # ------------------------------------------------------
    # Extra step
    # ------------------------------------------------------
    # ~ @http.route(['/shop/extra_info'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def extra_info(self, **post):
        return super(WebsiteSale, self).extra_info(**post)

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
        return(WebsiteSale, self).payment(**post)
        
    # ~ @http.route(['/shop/payment/transaction/',
        # ~ '/shop/payment/transaction/<int:so_id>',
        # ~ '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        return super(WebsiteSale, self).payment_transaction(acquirer_id, save_token, so_id, access_token, token, **kwargs)

    # ~ @http.route('/shop/payment/token', type='http', auth='public', website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def payment_token(self, pm_id=None, **kwargs):
       return super(WebsiteSale, self).payment_token(pm_id, **kwargs)

    # ~ @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def payment_get_status(self, sale_order_id, **post):
        return super(WebsiteSale, self).payment_get_status(sale_order_id, **post)

    # ~ @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        return super(WebsiteSale, self).payment_validate(transaction_id, sole_order_id, **post)
        
    # ~ @http.route(['/shop/terms'], type='http', auth="public", website=True, sitemap=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def terms(self, **kw):
        return super(WebsiteSale, self).terms(**kw)

    # ~ @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def payment_confirmation(self, **post):
       return super(WebsiteSale, self).payment_confirmation(**post)

    # ~ @http.route(['/shop/print'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def print_saleorder(self, **kwargs):
        return super(WebsiteSale, self).print_saleorder(**kwargs)

    # ~ @http.route(['/shop/tracking_last_order'], type='json', auth="public")
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def tracking_cart(self, **post):
        return super(WebsiteSale, self).tracking_cart(**post)

    # ------------------------------------------------------
    # Edit
    # ------------------------------------------------------

    # ~ @http.route(['/shop/add_product'], type='json', auth="user", methods=['POST'], website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def add_product(self, name=None, category=None, **post):
        return super(WebsiteSale, self).add_product(name, category, **post)

    # ~ @http.route(['/shop/change_sequence'], type='json', auth='user')
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def change_sequence(self, id, sequence):
        return super(WebsiteSale, self).change_sequence(id, sequence)

    # ~ @http.route(['/shop/change_size'], type='json', auth='user')
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def change_size(self, id, x, y):
        return super(WebsiteSale, self).change_size(id, x, y)

    # ~ @http.route(['/shop/change_ppg'], type='json', auth='user')
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def change_ppg(self, ppg):
        return super(WebsiteSale, self).change_ppg(ppg)

    # ~ @http.route(['/shop/change_ppr'], type='json', auth='user')
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def change_ppr(self, ppr):
        return super(WebsiteSale, self).change_ppr(ppr)

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

    # ~ @http.route(['/shop/country_infos/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def country_infos(self, country, mode, **kw):
        return super(WebsiteSale, self).country_infos(country, mode, **kw)

    # --------------------------------------------------------------------------
    # Products Search Bar
    # --------------------------------------------------------------------------

    # ~ @http.route('/shop/products/autocomplete', type='json', auth='public', website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def products_autocomplete(self, term, options={}, **kwargs):
        return super(WebsiteSale, self).products_autocomplete(term, options, **kwargs)
    # --------------------------------------------------------------------------
    # Products Recently Viewed
    # --------------------------------------------------------------------------
    # ~ @http.route('/shop/products/recently_viewed', type='json', auth='public', website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def products_recently_viewed(self, **kwargs):
        return super(WebsiteSale, self).products_recently_viewed(**kwargs)

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

    # ~ @http.route('/shop/products/recently_viewed_update', type='json', auth='public', website=True)
    # ~ @memcached.route(
        # ~ #key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        # ~ flush_type=lambda kw: 'webshop',
        # ~ no_cache=True,
        # ~ cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        # ~ max_age=31536000, # Webbläsare
        # ~ s_maxage=600)     # Varnish
    # ~ def products_recently_viewed_update(self, product_id, **kwargs):
        # ~ _logger.warning("RECENTLY VIEWED")
        # ~ _logger.warning(product_id)
        # ~ _logger.warning(kwargs)
        # ~ return super(WebsiteSale, self).products_recently_viewed_update(product_id, **kwargs)

    # ~ @http.route('/shop/products/recently_viewed_delete', type='json', auth='public', website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def products_recently_viewed_delete(self, product_id, **kwargs):
        return super(WebsiteSale, self).products_recently_viewed_delete(product_id, **kwargs)

    # --------------------------------------------------------------------------
    # Website Snippet Filters
    # --------------------------------------------------------------------------

    # ~ @http.route('/website_sale/snippet/options_filters', type='json', auth='user', website=True)
    @memcached.route(
        # ~ key=lambda kw: u'db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country}%s group: %s webshop_type: %s%s' % (request.website.get_search_values(kw), request.website.get_dn_groups(), request.website.get_webshop_type(kw), request.website.dn_handle_webshop_session(kw.get('category'), kw.get('preset'), {}, require_cat_preset=False) or ''),
        flush_type=lambda kw: 'webshop',
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000, # Webbläsare
        s_maxage=600)     # Varnish
    def get_dynamic_snippet_filters(self):
        return super(WebsiteSale, self).get_dynamic_snippet_filters()








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

