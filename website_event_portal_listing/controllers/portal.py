# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request
import werkzeug


class PortalEvent(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        EventAttendee = request.env['event.registration'].sudo()
        if 'event_count' in counters:
            event_count = EventAttendee.search_count(self._get_event_domain()) \
                if EventAttendee.check_access_rights('read', raise_exception=False) else 0
            values['event_count'] = event_count
        return values

    def _get_event_domain(self):
        partner = request.env.user.partner_id
        return [('email', '=', partner.email)]
        # return [('partner_id', '=', partner.commercial_partner_id.id)]

    @http.route(['/my/events', '/my/events/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_events(self, page=1, date_open=None, date_closed=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        EventAttendee = request.env['event.registration'].sudo()

        domain = self._get_event_domain()

        searchbar_sortings = {
            'date_open': {'label': _('Date'), 'order': 'date_open desc'},
            'date_closed': {'label': _('Due Date'), 'order': 'date_closed desc'},
            'name': {'label': _('Event'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date_open'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_open and date_closed:
            domain += [('date_open', '>', date_open), ('date_closed', '<=', date_closed)]

        # count for pager
        event_count = EventAttendee.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/events",
            url_args={'date_open': date_open, 'date_closed': date_closed, 'sortby': sortby},
            total=event_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        events = EventAttendee.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_events_history'] = events.ids[:100]

        values.update({
            'date': date_open,
            'events': events,
            'page_name': 'events',
            'pager': pager,
            'default_url': '/my/events',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("website_event_portal_listing.portal_my_events", values)


class WebsiteEventControllerExtended(WebsiteEventController):
    @http.route(['''/my/event/<int:event_id>'''], type='http', auth="public", website=True)
    def event_details(self, event_id, **post):
        event = request.env['event.event'].sudo().browse(event_id)
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        attendees_sudo = request.env['event.registration'].sudo().search([
            ('event_id', '=', event.id), ('email', '=', request.env.user.partner_id.email)
        ])

        return request.render("website_event_portal_listing.event_info",
                              self._get_registration_confirm_values(event, attendees_sudo))
