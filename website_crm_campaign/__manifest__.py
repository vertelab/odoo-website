# Copyright (C) 2025 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Website CRM Campaign',
    'version': '18.0.1.0.0',
    'category': 'Marketing/Campaigns',
    'summary': 'Publish CRM campaigns on website.',
    'description': '''
Website CRM Campaign
====================

    Publish CRM campaigns on website.

    Features:

        - UI Integration: Extends 2 view(s) in the Odoo interface.
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-website/website_crm_campaign',
    'license': 'AGPL-3',
    'depends': ['website_sale', 'sale_crm', 'crm_campaign_product'],
    'data': [
        'views/website_crm_campaign_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_crm_campaign/static/src/css/sale_campaign.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
