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
# Part of Softhealer Technologies.

{
    'name': 'Website: Document Activities',
    'version': '14.0.1.3',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'User can see events registered for.',
    'category': 'Website',
    "description": """
    User can see activities from the portal.
    14.0.1.3 - Removed 'Actions' from this module and moved to new module.
    14.0.1.2 - Link to the activities document.
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-website/website_document_activities/',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-website',
    'depends': ['portal', 'sale', 'project', 'toggle_record_on_portal', 'record_keeping_project', 'web_editor'],
    "data": [
        'views/portal_template.xml',
        'views/sale_portal_templates.xml',
        'views/project_portal_templates.xml',
        'views/assets.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
