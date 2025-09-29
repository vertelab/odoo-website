# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.osv import expression
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)

class AccountMove(PortalAccount):
    def _prepare_home_portal_values(self, counters):
        _logger.error(f"toggle_record_on_portal module loaded {counters=}")

        values = super()._prepare_home_portal_values(counters)

        domain = self._get_invoices_domain('out')
        domain += [('show_on_customer_portal', '=', True)]
        domain += [('partner_id', '=', request.env.user.partner_id.id)]

        if 'overdue_invoice_count' in counters:
            values['overdue_invoice_count'] = self._get_overdue_invoice_count()
        if 'invoice_count' in counters:
            invoice_count = request.env['account.move'].search_count(domain, limit=1) \
                if request.env['account.move'].has_access('read') else 0
            values['invoice_count'] = invoice_count
        if 'bill_count' in counters:
            bill_count = request.env['account.move'].search_count(self._get_invoices_domain('in'), limit=1) \
                if request.env['account.move'].has_access('read') else 0
            values['bill_count'] = bill_count
        return values

    #
    # @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
    #     values = self._prepare_portal_layout_values()
    #     AccountInvoice = request.env['account.move']
    #
    #     domain = self._get_invoices_domain()
    #     domain += [('show_on_customer_portal', '=', True)]
    #     domain += [('partner_id', '=', request.env.user.partner_id.id)]
    #
    #     searchbar_sortings = {
    #         'date': {'label': _('Date'), 'order': 'invoice_date desc'},
    #         'duedate': {'label': _('Due Date'), 'order': 'invoice_date_due desc'},
    #         'name': {'label': _('Reference'), 'order': 'name desc'},
    #         'state': {'label': _('Status'), 'order': 'state'},
    #     }
    #     # default sort by order
    #     if not sortby:
    #         sortby = 'date'
    #     order = searchbar_sortings[sortby]['order']
    #
    #     searchbar_filters = {
    #         'all': {'label': _('All'), 'domain': []},
    #         'invoices': {'label': _('Invoices'), 'domain': [('move_type', 'in', ('out_invoice', 'out_refund'))]},
    #         'bills': {'label': _('Bills'), 'domain': [('move_type', '=', ('in_invoice', 'in_refund'))]},
    #     }
    #     # default filter by value
    #     if not filterby:
    #         filterby = 'all'
    #     domain += searchbar_filters[filterby]['domain']
    #
    #     if date_begin and date_end:
    #         domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
    #
    #     # count for pager
    #     invoice_count = AccountInvoice.search_count(domain)
    #     # pager
    #     pager = portal_pager(
    #         url="/my/invoices",
    #         url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
    #         total=invoice_count,
    #         page=page,
    #         step=self._items_per_page
    #     )
    #     # content according to pager and archive selected
    #     invoices = AccountInvoice.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
    #     request.session['my_invoices_history'] = invoices.ids[:100]
    #
    #     values.update({
    #         'date': date_begin,
    #         'invoices': invoices,
    #         'page_name': 'invoice',
    #         'pager': pager,
    #         'default_url': '/my/invoices',
    #         'searchbar_sortings': searchbar_sortings,
    #         'sortby': sortby,
    #         'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
    #         'filterby': filterby,
    #     })
    #     return request.render("account.portal_my_invoices", values)

    def _prepare_my_invoices_values(self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/invoices"):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env['account.move']

        domain = expression.AND([
            domain or [],
            self._get_invoices_domain(),
        ])

        domain += [('show_on_customer_portal', '=', True)]
        domain += [('partner_id', '=', request.env.user.partner_id.id)]

        searchbar_sortings = self._get_account_searchbar_sortings()
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = self._get_account_searchbar_filters()
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        values.update({
            'date': date_begin,
            # content according to pager and archive selected
            # lambda function to get the invoices recordset when the pager will be defined in the main method of a route
            'invoices': lambda pager_offset: (
                [
                    invoice._get_invoice_portal_extra_values()
                    for invoice in AccountInvoice.search(
                        domain, order=order, limit=self._items_per_page, offset=pager_offset
                    )
                ]
                if AccountInvoice.has_access('read') else
                AccountInvoice
            ),
            'page_name': 'invoice',
            'pager': {  # vals to define the pager.
                "url": url,
                "url_args": {'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
                "total": AccountInvoice.search_count(domain) if AccountInvoice.has_access('read') else 0,
                "page": page,
                "step": self._items_per_page,
            },
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'overdue_invoice_count': self._get_overdue_invoice_count(),
        })
        return values