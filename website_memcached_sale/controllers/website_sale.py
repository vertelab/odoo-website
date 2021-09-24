import logging
from odoo import http
from odoo.http import request
from odoo.service import common
from odoo import models, fields, api, _
from odoo.addons.website_memcached import memcached
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    # @http.route([
    # '''/shop''',
    # '''/shop/page/<int:page>''',
    # '''/shop/category/<model("product.public.category"):category>''',
    # '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    # ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    @memcached.route(
        key=lambda parameters: "db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} search: %s pricelist: %s attribs: %s order: %s"
        % (
            str(parameters.get("search")),
            request.website.get_pricelist(),
            request.website.get_attribs(),
            str(parameters.get("order")),
        ),
        flush_type=lambda kw: "webshop",
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000,  # Webbläsare
        s_maxage=600,  # Varnish
    )
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        return super(WebsiteSale, self).shop(page, category, search, ppg, **post)

    # @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    @memcached.route(
        key=lambda parameters: "db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country} params: %s pricelist: %s"
        % (str(parameters).strip("{}"), request.website.get_pricelist()),
        flush_type=lambda kw: "webshop",
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000,  # Webbläsare
        s_maxage=600,  # Varnish
    )
    def product(self, product, category="", search="", **kwargs):
        return super(WebsiteSale, self).product(product, category, search, **kwargs)

    # @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=False)
    @memcached.route(
        key=lambda parameters: "db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country} params: %s pricelist: %s"
        % (str(parameters).strip("{}"), request.website.get_pricelist()),
        flush_type=lambda kw: "webshop",
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000,  # Webbläsare
        s_maxage=600,  # Varnish
    )
    def old_product(self, product, category="", search="", **kwargs):
        # Compatibility pre-v14
        return super(WebsiteSale, self).old_product(product, category, search, **kwargs)

    # @http.route(['/shop/terms'], type='http', auth="public", website=True, sitemap=True)
    @memcached.route(
        key=lambda parameters: "db: {db} publisher: {publisher} base.group_website_designer: {designer} path: {path} logged_in: {logged_in} lang: {lang} country: {country} params: %s pricelist: %s"
        % (str(parameters).strip("{}"), request.website.get_pricelist()),
        flush_type=lambda kw: "webshop",
        no_cache=True,
        cache_age=86400,  # Memcached    43200 (12 tim)  86400 (24 tim)  31536000 (1 år)
        max_age=31536000,  # Webbläsare
        s_maxage=600,  # Varnish
    )
    def terms(self, **kw):
        return super(WebsiteSale, self).terms(**kw)
