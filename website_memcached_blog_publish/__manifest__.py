# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2018- Vertel AB (<http://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "DEPRECATED! Website MemCached Blog",
    "version": "1.0",
    "category": "other",
    "summary": "website acceleration for blog using memcached",
    "description": """
Add mechanisms to cache rendered blog pages
This module depends on website_memcached

""",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "website": "http://www.vertel.se",
    "depends": ["website_memcached", "website_blog"],
    "external_dependencies": {
        "python": [
            "pymemcache",
        ]
    },
    "data": [
        "website_view.xml",
    ],
    "installable": True,
    "application": False,
}
