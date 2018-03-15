{
    'name': 'Multi Website Product domain',
    'category': 'Website',
    'summary': 'Build Multiple Websites and add a product domain',
    'website': 'http://www.vertel.se',
    'version': '1.0',
    'description': """
Multi Website Product domain
============================

        """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'depends': ['website_multi','website_sale'],
    'installable': True,
    'data': [
        'res_config.xml',
        'website_views.xml',
    ],
    'demo' : [
    ],
    'application': True,
}
