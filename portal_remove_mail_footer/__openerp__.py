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
    'name': 'Portal Remove Mail Footer',
    'version': '0.2',
    'category': '',
    'summary': "",
    'description': """
        
        When sending mail to a partner the mail has a link in the footer to the object
        a) if there is no res.users created for this partner and portal_remove_mail_footer.portal is set to 0, if it is set to 1 no footer link is generated
        b) if the partner already has a res.users footer will be sent if portal_remove_mail_footer.mail is set to 0, if it is set to 1 no footer link is generated
        
""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['portal'],
    'data': [
        'data.xml',
    ],
    'application': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
