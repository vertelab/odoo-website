# -*- coding: utf-8 -*-
{
    'name': 'eLearning with Scorm',
    'version': '1.2',
    'sequence': 10,
    'summary': 'Manage and publish an eLearning platform',
    'website': 'https://www.manprax.com',
    'author': 'ManpraX Software LLP',
    'category': 'Website/eLearning',
    'description': """
Create Online Courses Using Scorm
""",
    'depends': [
        'website_slides',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/slide_slide_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_scorm_elearning/static/src/js/slides_course.js',
            'website_scorm_elearning/static/src/js/slides_course_fullscreen_player.js',
            'website_scorm_elearning/static/src/xml/website_slides_fullscreen.xml',
        ],
    },
    'demo': [],
    'qweb': [],
    'images': ["static/description/images/scorm_banner.png"],
    'installable': True,
    'application': True,
    'license': 'AGPL-3',
}
