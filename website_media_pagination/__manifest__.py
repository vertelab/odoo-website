{
    'name': 'Website Media Pagination',
    'version': '18.0.1.1.0',
    'category': 'Website',
    'summary': 'Add pagination to website media library dialog',
    'depends': ['website'],
    'assets': {
        'web.assets_frontend': [
            'website_media_pagination/static/src/scss/media_pagination.scss',
        ],
        'website.assets_wysiwyg': [
            'website_media_pagination/static/src/js/media_pagination.js',
            'website_media_pagination/static/src/xml/media_pagination.xml',
        ],
    },
    'auto_install': False,
    'installable': True,
    'license': 'LGPL-3',
}
