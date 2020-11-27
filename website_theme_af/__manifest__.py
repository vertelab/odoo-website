{
    "name": "AF Website Tema V12",
    "summary": "AF Website Theme V12	",
    "version": "12.0.0.3",
    "category": "Theme/Website",
    "description": """
		AF Website tema för Odoo 12.0 community edition.
		12.0.0.3 -  This update adds changes to the main navigation to enable screen readers (A11y-update).
    """,
    "installable": True,
    "depends": [
        'portal', 'web_backend_theme_af', 'website'
    ],
    "data": [
        'views/assets.xml',
        'views/template.xml'
    ],
    'qweb': [
        "static/src/xml/menu.xml",
    ]
}
