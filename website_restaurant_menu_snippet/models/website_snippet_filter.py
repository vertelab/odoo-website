
from ast import literal_eval
from collections import OrderedDict
from itertools import groupby
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, MissingError
from odoo.osv import expression
from lxml import etree, html
import logging
from random import randint

_logger = logging.getLogger(__name__)


class WebsiteSnippetFilter(models.Model):
    _inherit = 'website.snippet.filter'

    product_cross_selling = fields.Boolean(string="About cross selling products", default=False,
        help="True only for product filters that require a product_id because they relate to cross selling")

    @api.model
    def _get_website_currency(self):
        pricelist = self.env['website'].get_current_website().get_current_pricelist()
        return pricelist.currency_id

    def _render_restaurant_data(self, template_key, limit, search_domain=None, with_sample=False):
        """Renders the website dynamic snippet items"""
        self.ensure_one()
        assert '.dynamic_filter_template_' in template_key, _(
            "You can only use template prefixed by dynamic_filter_template_ ")
        if search_domain is None:
            search_domain = []

        if self.website_id and self.env['website'].get_current_website() != self.website_id:
            return ''

        if self.model_name.replace('.', '_') not in template_key:
            return ''

        records = self._prepare_values(limit, search_domain)

        for rec in records:
            rec.update({
                'pos_categ_record': rec.get('_record')['pos_categ_id'],
                'pos_categ_name': rec.get('_record')['pos_categ_id']['name']
            })

        sorted_data = sorted(records, key=lambda x: x['pos_categ_name'])

        records = []
        for key, group in groupby(sorted_data, key=lambda x: x['pos_categ_name']):
            records.append({'Category': key, 'Items': list(group)})

        is_sample = with_sample and not records
        if is_sample:
            records = self._prepare_sample(limit)
        content = self.env['ir.qweb'].with_context(inherit_branding=False)._render(template_key, dict(
            records=records,
            is_sample=is_sample,
        ))
        return [etree.tostring(el, encoding='unicode') for el in
                html.fromstring('<root>%s</root>' % str(content)).getchildren()]
