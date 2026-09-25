# Copyright (C) 2025 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'CRM Campaign Blog',
    'version': '18.0.1.0.0',
    'category': 'Marketing/Campaigns',
    'summary': 'Link blog posts to CRM campaigns.',
    'description': '''
CRM Campaign Blog
=================

    Link blog posts to CRM campaigns.

    Features:

        - Focused Fix: A small, targeted improvement to standard Odoo behaviour.
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-website/crm_campaign_blog',
    'license': 'AGPL-3',
    'depends': ['crm_campaign_addons', 'website_blog'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
