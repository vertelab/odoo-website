# -*- coding: utf-8 -*-
{
    'name': 'Jitsi Meet Integration',
    'version': '8.0.1.0.0',
    'category': 'website',
    'sequence': 1,
    'summary': 'Handle Jitsi meetings for events.',
    'description': """
		Adds a new APP to create and share Jisti Meet video conference meetings between Odoo users. You can invite external users by sending mail from Odoo.
		When you join the meeting Odoo opens a new browser tab so you can keep working on Odoo, and share screen with your partners at Jisti Meet. 
    """,
    "author": "Vertel Ab, Sinerkia ID",
    "website": "https://vertel.se",
    "depends": [
        'base',
        'web',
        'mail',
        'calendar',
        'website',
        'email_template',
        'website_imagemagick',
        'website_event_dermanord',
        'website_event', 
        'theme_dermanord',  
        'website_partner_google_maps',
        'partner_token',
        ],
    "data": [
        'views/jitsi_meet_views.xml',
        'data/jitsi_meet.xml',
        'data/mail_template.xml',
        'security/ir.model.access.csv',
        'security/base_security.xml',
        'views/jitsi_templates.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
