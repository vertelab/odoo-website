# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import datetime
import json
import os
import logging
import re
import requests
import werkzeug.urls
import werkzeug.utils
import werkzeug.wrappers

from itertools import islice
from lxml import etree
from textwrap import shorten
from werkzeug.exceptions import NotFound
from xml.etree import ElementTree as ET

import odoo

from odoo import http, models, fields, _
from odoo.exceptions import AccessError
from odoo.http import request, SessionExpiredException
from odoo.osv import expression
from odoo.tools import OrderedSet, escape_psql, html_escape as escape
from odoo.addons.http_routing.models.ir_http import slug, slugify, _guess_mimetype
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.web import Home
from odoo.addons.web.controllers.binary import Binary
from odoo.addons.website.tools import get_base_domain

logger = logging.getLogger(__name__)


class Website(Home):

    @http.route('/restaurant/snippet/filters', type='json', auth='public', website=True)
    def custom_get_dynamic_filter(self, filter_id, template_key=None, limit=None, search_domain=None, with_sample=False):
        template_key = "website_restaurant_menu_snippet.dynamic_filter_template_pos_category_restaurant_menu_1"
        filter_template_id = request.env.ref('website_restaurant_menu_snippet.dynamic_filter_pos_categories')
        dynamic_filter = request.env['website.snippet.filter'].sudo().search(
            [('id', '=', filter_template_id.id)] + request.website.website_domain(), limit=1
        )
        return dynamic_filter and dynamic_filter._render_restaurant_data(template_key, limit, search_domain, with_sample) or []