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
                                           help="True only for product filters that require a product_id because they "
                                                "relate to cross selling")

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

        records = self._prepare_pos_category_values(limit, search_domain)

        is_sample = with_sample and not records
        if is_sample:
            records = self._prepare_sample(limit)
        content = self.env['ir.qweb'].with_context(inherit_branding=False)._render(template_key, dict(
            records=records,
            is_sample=is_sample,
        ))
        return [etree.tostring(el, encoding='unicode') for el in
                html.fromstring('<root>%s</root>' % str(content)).getchildren()]

    def _prepare_pos_category_values(self, limit=None, search_domain=None):
        """Gets the data and returns it the right format for render."""
        self.ensure_one()

        # The "limit" field is there to prevent loading an arbitrary number of
        # records asked by the client side. This here makes sure you can always
        # load at least 16 records as it is what the editor allows.
        max_limit = max(self.limit, 16)
        limit = limit and min(limit, max_limit) or max_limit

        if self.filter_id:
            filter_sudo = self.filter_id.sudo()
            domain = filter_sudo._get_eval_domain()
            if 'website_id' in self.env[filter_sudo.model_id]:
                domain = expression.AND([domain, self.env['website'].get_current_website().website_domain()])
            if 'company_id' in self.env[filter_sudo.model_id]:
                website = self.env['website'].get_current_website()
                domain = expression.AND([domain, [('company_id', 'in', [False, website.company_id.id])]])
            # if 'is_published' in self.env[filter_sudo.model_id]:
            #     domain = expression.AND([domain, [('is_published', '=', True)]])
            if search_domain:
                domain = expression.AND([domain, search_domain])
            try:
                records = self.env[filter_sudo.model_id].with_context(**literal_eval(filter_sudo.context)).search(
                    domain,
                    order=','.join(literal_eval(filter_sudo.sort)) or None,
                    limit=limit
                )
                return self._filter_records_to_values(records)
            except MissingError:
                _logger.warning("The provided domain %s in 'ir.filters' generated a MissingError in '%s'", domain, self._name)
                return []
        elif self.action_server_id:
            try:
                return self.action_server_id.with_context(
                    dynamic_filter=self,
                    limit=limit,
                    search_domain=search_domain,
                ).sudo().run() or []
            except MissingError:
                _logger.warning("The provided domain %s in 'ir.actions.server' generated a MissingError in '%s'", search_domain, self._name)
                return []