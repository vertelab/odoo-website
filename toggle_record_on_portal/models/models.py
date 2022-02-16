from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_on_customer_portal = fields.Boolean(string="Show on Customer Portal")


class Invoices(models.Model):
    _inherit = 'account.move'

    show_on_customer_portal = fields.Boolean(string="Show on Customer Portal")


class Event(models.Model):
    _inherit = 'event.registration'

    show_on_customer_portal = fields.Boolean(string="Show on Customer Portal")


class ProjectProject(models.Model):
    _inherit = 'project.project'

    show_on_customer_portal = fields.Boolean(string="Show on Customer Portal")


class ProjectTask(models.Model):
    _inherit = 'project.task'

    show_on_customer_portal = fields.Boolean(string="Show on Customer Portal")


class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    show_on_customer_portal = fields.Boolean(string="Show on Customer Portal")
