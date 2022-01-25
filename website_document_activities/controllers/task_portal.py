
from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
# from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.project.controllers.portal import CustomerPortal, portal_pager

from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    @http.route(['/my/tasks/activities', '/my/tasks/activities/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tasks_activities(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                        search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()

        project_task = request.env['project.task'].search([], limit=self._items_per_page) \
            if request.env['project.task'].check_access_rights('read', raise_exception=False) else 0

        # task count
        task_count = len(project_task.mapped('activity_ids'))

        # pager
        pager = portal_pager(
            url="/my/tasks/activities",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby,
                      'groupby': groupby, 'search_in': search_in, 'search': search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )

        grouped_tasks = [tasks for tasks in project_task if tasks.activity_ids]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'grouped_tasks': grouped_tasks,
            'page_name': 'task',
            'default_url': '/my/tasks/activities',
            'pager': pager,
        })
        return request.render("website_document_activities.portal_my_tasks", values)

    @http.route(['/my/projects/activities', '/my/projects/activities/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_projects_activities(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()

        project_activities = request.env['mail.activity'].sudo().search([('res_model', '=', 'project.project')])

        project_ids = []

        for activities in project_activities:
            project_ids.append(request.env['project.project'].browse(activities.res_id))

        # projects count
        project_count = len(set(project_ids))

        # pager
        pager = portal_pager(
            url="/my/projects/activities",
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        projects = set(project_ids)

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'page_name': 'project',
            'default_url': '/my/projects/activities',
            'pager': pager,
            'sortby': sortby
        })
        return request.render("project.portal_my_projects", values)
