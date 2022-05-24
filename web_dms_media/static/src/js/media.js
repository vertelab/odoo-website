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


    ajax.loadXML('/web_dms_media/static/src/xml/wysiwyg.xml', QWeb);

    MediaWidget.extend({
        xmlDependencies: ['/web_editor/static/src/xml/wysiwyg.xml', '/web_dms_media/static/src/xml/wysiwyg.xml'],
    })


    FileWidget.include({
        events: _.extend({}, FileWidget.prototype.events, {
            'click .o_show_more': '_onShowMoreContent',
        }),

        _getDMSAttachmentsDomain: function (needle) {
            var domain = []
            domain = domain.concat(this.options.mimetypeDomain);
            if (needle && needle.length) {
                domain.push('|', ['name', 'ilike', needle], ['directory_id.name', 'ilike', needle]);
            }
            return domain;
        },

        _attachmentInfo: async function (number, offset) {
            return this._rpc({
                model: 'dms.file',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: this._getDMSAttachmentsDomain(this.needle),
                    order: [{name: 'id', asc: false}],
                    context: this.options.context,
                    // Try to fetch first record of next page just to know whether there is a next page.
                    limit: number,
                    offset: offset,
                },
            }).then(attachments => {
                return attachments
            });
        },

        getTotalCount: async function () {
            return this._rpc({
                model: 'dms.file',
                method: 'search_read',
                args: [],
                kwargs: {
                    domain: this._getDMSAttachmentsDomain(this.needle),
                    order: [{name: 'id', asc: false}],
                    context: this.options.context,
                },
            }).then(attachments => {
                return attachments
            });
        },

        // returns range(1, 3) ==> [1, 2, 3]
        range: function (_start_, _end_) {
            return (new Array(_end_ - _start_ + 1)).fill(undefined).map((_, k) =>k + _start_);
        },

        fetchAttachments: async function (number, offset) {
            // get total record on the model (domains and context considered)
            this.total_record_count = await this.getTotalCount() 

             // get record based on limit and offset (domains and context considered)
            let attachments = await this._attachmentInfo(number, offset)         
            
            // compute page range depending on the total record and the limit set
            if (this.total_record_count.length > number) {
                const page_count = parseInt(Math.ceil(parseFloat(this.total_record_count.length / number)))
                this.page_range = this.range(1, page_count)
            } else {
                this.page_range = []
            }

            // render the buttons after attachment is listed           
            this.$('.o_load_more_ex').html(
                QWeb.render('wysiwyg.widgets.page.button', {widget: this})
            );
            this.attachments = attachments;

            // always set attachment to empty array
            Array.prototype.splice.apply([], [offset, attachments.length].concat(attachments));

            // // update color of active button
            // $('#'+this.current_button_id).css('background-color', '#7C7BAD !important');
            // $('#'+this.current_button_id).css('color', '#FFF !important');
        },

        _renderExisting: function (attachments) {
            return QWeb.render(this.existingAttachmentsTemplate, {
                attachments: attachments,
                widget: this,
            });
        },

        _onShowMoreContent: function (event) {
            let current_page = parseInt(event.target.innerText)

            this.current_button_id = event.target.id
            
            let offset = 0
            // compute offset if current_page is not 1 --- ((10 * 2) - 10) + 1 = 11
            if (current_page > 1) {
                offset = ((this.numberOfAttachmentsToDisplay * current_page) - this.numberOfAttachmentsToDisplay) + 1
            }

            return this.fetchAttachments(this.numberOfAttachmentsToDisplay, offset).then(() => {
                this._renderThumbnails();
                return Promise.resolve();                
            });
        },

        _loadMoreImages: function (event) {
            return
        },

    })

    ImageWidget.include({
        events: _.extend({}, ImageWidget.prototype.events, {
            'click .o_show_more': '_onShowMoreContent',
        }),

        _renderExisting: function (attachments) {
            if (this.needle && this.searchService !== 'database') {
                attachments = attachments.slice(0, this.MAX_DB_ATTACHMENTS);
            }
            return QWeb.render(this.existingAttachmentsTemplate, {
                attachments: attachments,
                libraryMedia: this.libraryMedia,
                widget: this,
            });
        },

        _onShowMoreContent: function (event) {
            let current_page = parseInt(event.target.innerText)

            this.current_button_id = event.target.id
            
            let offset = 0
            // compute offset if current_page is not 1 --- ((10 * 2) +  (-10-1)) + 1 = 10
            if (current_page > 1) {
                offset = ((this.numberOfAttachmentsToDisplay * current_page) + (-this.numberOfAttachmentsToDisplay - 1)) + 1
            }

            return this.fetchAttachments(this.numberOfAttachmentsToDisplay, offset).then(() => {
                this._renderThumbnails();
                return Promise.resolve();                
            });
        },
    })
})
