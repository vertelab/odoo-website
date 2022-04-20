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
        14.0.1.3 - Removed 'Actions' from this module and moved to new module
        14.0.1.2 - Link to the activities document
    """,
    "version": "14.0.1.3",
    "depends": ['portal', 'sale', 'project', 'toggle_record_on_portal', 'record_keeping_project', 'web_editor'],
    "data": [
        'views/portal_template.xml',
        'views/sale_portal_templates.xml',
        'views/project_portal_templates.xml',
        'views/assets.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
}
