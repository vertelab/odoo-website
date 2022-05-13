from odoo import http
from odoo.http import request
from odoo.service import common
from odoo import models, fields, api, _
from odoo.addons.web.controllers.main import Database, DataSet, Session, WebClient

import logging
_logger = logging.getLogger(__name__)


class DatabaseInherit(Database):

    @http.route('/web/database/list', type='json', auth='none', cors="*")
    def list(self):
        result = super(DatabaseInherit, self).list()
        _logger.warning(f"list: {result=}")
        return result


class DataSetInherit(DataSet):

    @http.route('/web/dataset/search_read', type='json', auth='user', cors="*")
    def search_read(self, model, fields=False, offset=0, limit=False, domain=None, sort=None):
        result = super().search_read(model, fields, offset, limit, domain, sort)
        _logger.warning(f"search_read: {result=}")
        return result


class SessionInherit(Session):

    @http.route('/web/session/authenticate', type='json', auth="none", cors="*")
    def authenticate(self, db, login, password, base_location=None):
        result = super(SessionInherit, self).authenticate(
            db, login, password, base_location)
        _logger.warning(f"authenticate: {result=}")
        return result

    @http.route('/web/session/get_session_info', type='json', auth="none", cors="*")
    def get_session_info(self):
        result = super(SessionInherit, self).get_session_info()
        _logger.warning(f"get_session_info: {result=}")
        return result


class WebClientInherit(WebClient):

    @http.route('/web/webclient/version_info', type='json', auth="none", cors="*")
    def version_info(self):
        result = super(WebClientInherit, self).version_info()
        _logger.warning(f"version_info: {result=}")
        return result
