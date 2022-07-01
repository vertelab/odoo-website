# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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
    'name': 'Website: Select2 Search Field',
    'version': '0.1',
    'category': '',
    'summary': "Adds a select2 search field.",
    'description': """Due to a naming conflict all instances of select2 have been rebranded as select9.
Manual can be found at https://select2.github.io/
""",
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/',
    'images': ['static/description/banner.png'], # 560x280 px.
    'depends': ['website'],
    'data': [
        'select2_template.xml',
    ],
    'application': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
