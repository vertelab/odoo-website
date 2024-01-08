# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Website: Restaurant Menu Snippet',
    'version': '17.0.0.0.0',
    'summary': 'Makes it easy to archive information.',
    'category': 'Website',
    'description': """
        Use Pos category to sort the meny.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-website/website_restaurant_menu_snippet',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-website',
    'depends': ['website', 'point_of_sale', 'pos_restaurant'],
    'data': [
        'views/snippets/s_restaurant_menu_snippet.xml',
        'data/product_snippet_template_data.xml',
        'views/pos_view.xml',
    ],
    'assets': {
        'website.assets_wysiwyg': [
            'website_restaurant_menu_snippet/static/src/snippets/s_restaurant_menu_snippet/options.js',
        ],
    },
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
