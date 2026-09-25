{
    'website': 'https://vertel.se/apps/odoo-website/website_gallery_fix',
    'name': 'Website Gallery Template Fix',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Fix duplicate gallery.slideshow template.',
    'description': '''
Website Gallery Template Fix
============================

    Fix duplicate gallery.slideshow template.

    Features:

        - Focused Fix: A small, targeted improvement to standard Odoo behaviour.
    ''',
    'depends': ['website'],
    'assets': {
        'website.assets_wysiwyg': [
            ('remove', 'website/static/src/snippets/s_image_gallery/000.xml'),
        ],
    },
    'auto_install': False,
    'installable': True,
    'license': 'LGPL-3',
}