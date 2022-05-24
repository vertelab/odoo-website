# Part of Softhealer Technologies.
{
    "name": "Website MediaBank User Groups",
    "author": "Vertel AB",
    "website": "https://www.vertel.se",
    "category": "Website",
    "license": "OPL-1",
    "summary": "Only the right group will be able to use the website media",
    "description": """
        User with the right group will use the website media
    """,
    "version": "14.0.1.2",
    "depends": ['website', 'web_editor'],
    "data": [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
