odoo.define('web_dms_media.web_media_bank', function (require) {
    'use strict';

    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');


    var MediaWidget = require('wysiwyg.widgets.media').MediaWidget
    var ImageWidget = require('wysiwyg.widgets.media').ImageWidget
    var FileWidget = require('wysiwyg.widgets.media').FileWidget

    const {getCSSVariableValue, DEFAULT_PALETTE} = require('web_editor.utils');


    ajax.loadXML('/web_dms_media/static/src/xml/wysiwyg.xml', QWeb);


    // console.log(MediaWidget)
    //
    MediaWidget.extend({
        xmlDependencies: ['/web_editor/static/src/xml/wysiwyg.xml', '/web_dms_media/static/src/xml/wysiwyg.xml'],

    })


    FileWidget.include({
        _getDMSAttachmentsDomain: function (needle) {
            var domain = []
            domain = domain.concat(this.options.mimetypeDomain);
            if (needle && needle.length) {
                domain.push('|', ['name', 'ilike', needle], ['directory_id.name', 'ilike', needle]);
            }
            return domain;
        },

        fetchAttachments: function (number, offset) {
            return this._rpc({
                model: 'dms.file',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: this._getDMSAttachmentsDomain(this.needle),
                    order: [{name: 'id', asc: false}],
                    context: this.options.context,
                    // Try to fetch first record of next page just to know whether there is a next page.
                    limit: number + 1,
                    offset: offset,
                },
            }).then(attachments => {
                console.log('attachments', attachments)
                this.attachments = this.attachments.slice();
                Array.prototype.splice.apply(this.attachments, [offset, attachments.length].concat(attachments));
            });
        },

        _renderExisting: function (attachments) {
            console.log('FileWidget****', attachments)
            console.log('FileWidget****', this)
            return QWeb.render(this.existingAttachmentsTemplate, {
                attachments: attachments,
                widget: this,
            });
        },



    })

    ImageWidget.include({
        _renderExisting: function (attachments) {
            if (this.needle && this.searchService !== 'database') {
                attachments = attachments.slice(0, this.MAX_DB_ATTACHMENTS);
            }
            console.log('ImageWidget****', attachments)
            console.log('ImageWidget this****', this)
            console.log('ImageWidget libraryMedia****', this.libraryMedia)
            return QWeb.render(this.existingAttachmentsTemplate, {
                attachments: attachments,
                libraryMedia: this.libraryMedia,
                widget: this,
            });
        },
    })
})
