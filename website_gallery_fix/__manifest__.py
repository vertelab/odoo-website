{
    'name': 'Website Gallery Template Fix',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Fix duplicate gallery.slideshow template',
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