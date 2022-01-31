odoo.define('wysiwyg.widgets.media.groups', function (require) {
    'use strict';

    var concurrency = require('web.concurrency');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var dom = require('web.dom');
    var fonts = require('wysiwyg.fonts');
    var utils = require('web.utils');
    var Widget = require('web.Widget');
    var session = require('web.session');

    const {removeOnImageChangeAttrs} = require('web_editor.image_processing');
    const {getCSSVariableValue, DEFAULT_PALETTE} = require('web_editor.utils');

    var QWeb = core.qweb;
    var _t = core._t;

    var FileWidget = require('wysiwyg.widgets.media').FileWidget;
    var MediaWidget = require('wysiwyg.widgets.media').MediaWidget;

    // FileWidget.include({
    //     willStart: function () {
    //         var self = this;
    //         var prom = this._rpc({
    //             route: '/user/status',
    //         });
    //         prom.then(function (result) {
    //             console.log("result", result)
    //             self.groups = result.groups;
    //         });
    //     }
    // })

    MediaWidget.include({
        xmlDependencies: (MediaWidget.prototype.xmlDependencies || []).concat(
            ['/website_mediabank_usergroups/static/src/xml/wysiwyg.xml']
        ),

        init: function (parent, media, options) {
            this._super.apply(this, arguments);
            this.media = media;
            this.$media = $(media);

            var self = this;
            var prom = this._rpc({
                route: '/user/status',
            });
            prom.then(function (result) {
                console.log("result", result)
                self.groups = result.groups;
            });
        },
    })
})



