/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { uniqueId } from "@web/core/utils/functions";
import { renderToString } from "@web/core/utils/render";
import { listenSizeChange, utils as uiUtils } from "@web/core/ui/ui_service";
import { rpc } from "@web/core/network/rpc";

import { markup } from "@odoo/owl";

const DEFAULT_NUMBER_OF_ELEMENTS = 4;
const DEFAULT_NUMBER_OF_ELEMENTS_SM = 1;

const DynamicSnippet = publicWidget.Widget.extend({
    selector: '.s_restaurant_menu',
    disabledInEditableMode: false,
    read_events: {
        'click [data-url]': '_onCallToAction',
    },

    init: function () {
        console.log("000.js: init")
        this._super.apply(this, arguments);

        this.data = [];
        this.renderedContent = '';
        this.isDesplayedAsMobile = uiUtils.isSmall();
        this.unique_id = uniqueId("s_dynamic_restaurant_snippet_");
        this.template_key = 's_dynamic_restaurant_snippet';

    },

    willStart: function () {
        console.log("000.js: willStart")
        return this._super.apply(this, arguments).then(
            () => Promise.all([
                this._fetchData(),
            ])
        );
    },

    start: function () {
        console.log("000.js: start")
        return this._super.apply(this, arguments)
            .then(() => {
                this._setupSizeChangedManagement(true);
                this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
                this._render();
                this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
            });
    },

    destroy: function () {
        console.log("000.js: destroy")
        this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
        this._toggleVisibility(false);
        this._setupSizeChangedManagement(false);
        this._clearContent();
        this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
        this._super.apply(this, arguments);
    },

    _clearContent: function () {
        console.log("000.js: _clearContent")
        const $templateArea = this.$el.find('.dynamic_snippet_template');
        this.trigger_up('widgets_stop_request', {
            $target: $templateArea,
        });
        $templateArea.html('');
    },

    _isConfigComplete: function () {
        console.log("000.js: _isConfigComplete")
        return this.$el.get(0).dataset.productCategoryId !== undefined && this.$el.get(0).dataset.numberOfRecords !== undefined;
    },

     _getCategorySearchDomain() {
        console.log("000.js: _getCategorySearchDomain")
        const searchDomain = [];
        let productCategoryId = this.$el.get(0).dataset.productCategoryId;
        if (productCategoryId && productCategoryId !== 'all') {
            if (productCategoryId === 'current') {
                productCategoryId = undefined;
                const productCategoryField = $("#product_details").find(".product_category_id");
                if (productCategoryField && productCategoryField.length) {
                    productCategoryId = parseInt(productCategoryField[0].value);
                }
                if (!productCategoryId) {
                    this.trigger_up('main_object_request', {
                        callback: function (value) {
                            if (value.model === "product.public.category") {
                                productCategoryId = value.id;
                            }
                        },
                    });
                }
                if (!productCategoryId) {
                    // Try with categories from product, unfortunately the category hierarchy is not matched with this approach
                    const productTemplateId = $("#product_details").find(".product_template_id");
                    if (productTemplateId && productTemplateId.length) {
                        searchDomain.push(['pos_categ_ids.product_tmpl_ids', 'in', parseInt(productTemplateId[0].value)]);
                    }
                }
            }
            if (productCategoryId) {
                searchDomain.push(['id', '=', parseInt(productCategoryId)]);
            }
        }
//        searchDomain.push(['available_in_pos', '=', true])
//        searchDomain.push(['available_in_pos', '=', true])
        return searchDomain;
    },

     _getSearchDomain: function () {
        console.log("000.js: _getSearhDomain")
        const searchDomain = this._getCategorySearchDomain();
        return searchDomain;
    },

    _getRpcParameters: function () {
        console.log("000.js: _getRpcParameters")
        return {};
    },

    async _fetchData() {
        console.log("000.js: _fetchData")
        if (this._isConfigComplete()) {
            const nodeData = this.el.dataset;
            const filterFragments = await rpc(
                '/restaurant/snippet/filters',
                {
                    'filter_id': parseInt(nodeData.filterId),
                    'template_key': `website_restaurant_menu_snippet.${nodeData.templateKey}`,
                    'limit': parseInt(nodeData.numberOfRecords),
                    'search_domain': this._getSearchDomain(),
                    'with_sample': this.editableMode,
                    ...this._getRpcParameters(),
                }
            );
            this.data = filterFragments.map(markup);
        } else {
            this.data = [];
        }
    },

    _prepareContent: function () {
        console.log("000.js: _prepareContent")
        this.renderedContent = renderToString(
            this.template_key,
            this._getQWebRenderOptions()
        );
    },

     _getQWebRenderOptions: function () {
        console.log("000.js: _getQWebRenderOptions")
        const dataset = this.el.dataset;
        const numberOfRecords = parseInt(dataset.numberOfRecords);
        let numberOfElements;
        if (uiUtils.isSmall()) {
            numberOfElements = parseInt(dataset.numberOfElementsSmallDevices) || DEFAULT_NUMBER_OF_ELEMENTS_SM;
        } else {
            numberOfElements = parseInt(dataset.numberOfElements) || DEFAULT_NUMBER_OF_ELEMENTS;
        }
        const chunkSize = numberOfRecords < numberOfElements ? numberOfRecords : numberOfElements;
        return {
            chunkSize: chunkSize,
            data: this.data,
            unique_id: this.unique_id,
            extraClasses: dataset.extraClasses || '',
        };
    },

    _render: function () {
        console.log("000.js: _render")
        if (this.data.length > 0 || this.editableMode) {
            this.$el.removeClass('o_dynamic_empty');
            this._prepareContent();
        } else {
            this.$el.addClass('o_dynamic_empty');
            this.renderedContent = '';
        }
        const classList = [...this.$el[0].classList];
        if (classList.includes('d-none') && !classList.some(className => className.match(/^d-(md|lg)-(?!none)/))) {
            this.$el[0].classList.remove('d-none');
        }
        this._renderContent();
        this.trigger_up('widgets_start_request', {
            $target: this.$el.children(),
            options: {parent: this},
            editableMode: this.editableMode,
        });
    },

    _renderContent: function () {
        console.log("000.js: _renderContent")
        const $templateArea = this.$el.find('.dynamic_snippet_template');
        this.trigger_up('widgets_stop_request', {
            $target: $templateArea,
        });
        $templateArea.html(this.renderedContent);
        this.trigger_up('widgets_start_request', {
            $target: $templateArea,
            editableMode: this.editableMode,
        });
    },

    _setupSizeChangedManagement: function (enable) {
        console.log("000.js: _setupSizeChangedManagement")
        if (enable === true) {
            this.removeSizeListener = listenSizeChange(this._onSizeChanged.bind(this));
        } else {
            this.removeSizeListener();
            delete this.removeSizeListener;
        }
    },

    _toggleVisibility: function (visible) {
        console.log("000.js: _toggleVisibility")
        this.$el.toggleClass('o_dynamic_empty', !visible);
    },


    _onCallToAction: function (ev) {
        console.log("000.js: _onCallToAction")
        window.location = $(ev.currentTarget).attr('data-url');
    },

    _onSizeChanged: function () {
        console.log("000.js: init")
        if (this.isDesplayedAsMobile !== uiUtils.isSmall()) {
            this.isDesplayedAsMobile = uiUtils.isSmall();
            this._render();
        }
    },
});

publicWidget.registry.dynamic_snippet = DynamicSnippet;

export default DynamicSnippet;
