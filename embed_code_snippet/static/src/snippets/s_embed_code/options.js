/** @odoo-module **/
odoo.define('embed_code_snippet.s_embed_code_options', function (require) {
    'use strict';

    var core = require('web.core');
    var Dialog = require('web.Dialog')
    var options = require('web_editor.snippets.options')


    const _t = core._t;

    options.registry.EmbedCode = options.Class.extend({
        //--------------------------------------------------------------------------
        // Options
        //--------------------------------------------------------------------------
        jsLibs: [
            '/web/static/lib/ace/ace.js',
            [
                '/web/static/lib/ace/mode-xml.js',
            ]
        ],

        async editCode() {
            const $container = this.$target.find('.s_embed_code_embedded');
            const code = $container.html().trim();

            await new Promise(resolve => {
                const $content = $(core.qweb.render('website.custom_code_dialog_content'));
                const aceEditor = this._renderAceEditor($content.find('.o_ace_editor_container')[0], code || '');
                const dialog = new Dialog(this, {
                    title: _t("Edit embedded code"),
                    $content,
                    buttons: [
                        {
                            text: _t("Save"),
                            classes: 'btn-primary',
                            click: async () => {
                                $container[0].innerHTML = aceEditor.getValue();
                            },
                            close: true,
                        },
                        {
                            text: _t("Discard"),
                            close: true,
                        },
                    ],
                });
                dialog.on('closed', this, resolve);
                dialog.open();
            });
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {DOMElement} node
         * @param {String} content text of the editor
         * @returns {Object}
         */
        _renderAceEditor(node, content) {
            const aceEditor = window.ace.edit(node);
            aceEditor.setTheme('ace/theme/monokai');
            aceEditor.setValue(content, 1);
            aceEditor.setOptions({
                minLines: 20,
                maxLines: Infinity,
                showPrintMargin: false,
            });
            aceEditor.renderer.setOptions({
                highlightGutterLine: true,
                showInvisibles: true,
                fontSize: 14,
            });

            const aceSession = aceEditor.getSession();
            aceSession.setOptions({
                mode: "ace/mode/xml",
                useWorker: false,
            });
            return aceEditor;
        },
    });
});
