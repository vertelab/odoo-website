# Part of Softhealer Technologies.
{
    "name": "Website Document Activities",
    "author": "Vertel",
    "website": "https://www.vertel.se",
    "category": "Website",
    "license": "OPL-1",
    "summary": "User can see events registered for.",
    "description": """
        User can see activities from the portal \n	
    """,
    "version": "14.0.1.1",
    "depends": ['portal', 'sale', 'project'],
    "data": [
        'views/portal_template.xml',
        'views/sale_portal_templates.xml',
        'views/project_portal_templates.xml',
        # 'views/document_portal_templates.xml',
        'views/assets.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
