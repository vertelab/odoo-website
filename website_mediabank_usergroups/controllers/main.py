# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class WebsiteBackend(http.Controller):

    @http.route('/user/status', type="json", auth='user')
    def fetch_user_status(self):
        has_group_system = request.env.user.has_group('base.group_system')
        has_group_designer = request.env.user.has_group('website.group_website_designer')
        has_group_publisher = request.env.user.has_group('website.group_website_publisher')
        user_group = {
            'groups': {
                'system': has_group_system,
                'website_designer': has_group_designer,
                'website_publisher': has_group_publisher
            },
        }
        print(user_group)
        return user_group
