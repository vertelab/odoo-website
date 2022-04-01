{
    "name": "DMS Files on Website Media",
    "author": "Vertel",
    "website": "https://www.vertel.se",
    "category": "Website",
    "license": "OPL-1",
    "summary": "User can see dms.file on the website media bank.",
    "description": """
        User can see dms.file on the website media bank \n	
    """,
    "version": "14.0.0.1",
    "depends": ['web_editor', 'base_setup', 'dms', 'website'],
    "data": [
        "views/assets.xml",
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    "auto_install": False,
}
