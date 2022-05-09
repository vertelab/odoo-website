import logging

from odoo import _
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.tools import consteq

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):
    def _document_check_access(self, model_name, document_id, access_token=None):
        """
        Intended to stop a user with knowledge of the id from accessing a sale order in 'draft' state.
        """
        _logger.warning("Entering customer portal _document_check_access")
        document_sudo = super(CustomerPortal, self)._document_check_access(model_name, document_id, access_token)
        if model_name == "sale.order":
            _logger.warning("Is a sale order")
            if access_token and document_sudo.access_token and consteq(document_sudo.access_token, access_token):
                _logger.warning("Has access token")
                # Has access due to access token
                return document_sudo
            elif document_sudo.state in ["draft"]:
                _logger.warning("is in draft")
                raise AccessError(_("Access Error, state in draft"))
        return document_sudo
