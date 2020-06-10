# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2020 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Jitsi Meet Event Integration',
    'version': '8.0.1.0.0',
    'category': 'website',
    'sequence': 1,
    'summary': 'Handle Jitsi meetings for events.',
    'description': """
		Adds a new APP to create and share Jisti Event video conference meetings between Odoo users. You can invite external users by sending mail from Odoo.
		When you join the meeting Odoo opens a new browser tab so you can keep working on Odoo, and share screen with your partners at Jisti Meet. 
    """,
    "author": "Vertel AB",
    "website": "https://vertel.se",
    "depends": [
        'jitsi_meet',
        'event_participant',
        ],
    "data": [
        'views/jitsi_event_views.xml',
        'data/mail_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
