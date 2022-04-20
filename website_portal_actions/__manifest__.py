# Part of Softhealer Technologies.
{
    "name": "Website Portal Actions",
    "author": "Vertel",
    "website": "https://www.vertel.se",
    "category": "Website",
    "license": "OPL-1",
    "summary": "User can see events registered for.",
    "description": """
        User can see actions from the portal \n
    """,
    "version": "14.0.0.0",
    "depends": ['portal', 'web_editor', 'website_document_activities'],
   # "depends": ['portal'], #, 'sale', 'project', 'toggle_record_on_portal', 'record_keeping_project'],
    "data": [
        'views/assets.xml',
        'views/portal_template.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
