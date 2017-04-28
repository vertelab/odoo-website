# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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

from openerp import api, models, fields, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

import logging
_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        if partner and not partner.user_ids and self.env['ir.config_parameter'].get_param('portal_remove_mail_footer.portal', '1') != '0':
            #Portal footer
            return super(MailMail, self)._get_partner_access_link(mail, partner=partner)
        if partner and partner.user_ids and self.env['ir.config_parameter'].get_param('portal_remove_mail_footer.mail', '1') != '0':
            #Mail footer
            return super(MailMail, self)._get_partner_access_link(mail, partner=partner)
        else:
            return None

