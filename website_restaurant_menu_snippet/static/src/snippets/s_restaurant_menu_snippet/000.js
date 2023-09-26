odoo.define('website_restaurant_menu_snippet.s_dynamic_snippet_restaurant_menu', function (require) {
    'use strict';

    const core = require('web.core');
    const config = require('web.config');
    const publicWidget = require('web.public.widget');
    const {Markup} = require('web.utils');
    const DEFAULT_NUMBER_OF_ELEMENTS = 4;
    const DEFAULT_NUMBER_OF_ELEMENTS_SM = 1;

    const DynamicSnippet = publicWidget.Widget.extend({
        selector: '.s_restaurant_menu',
        disabledInEditableMode: false,

        init: function () {
            this._super.apply(this, arguments);

            this.data = [];
            this.renderedContent = '';
            this.isDesplayedAsMobile = config.device.isMobile;
            this.uniqueId = _.uniqueId('s_dynamic_restaurant_snippet_');
            this.template_key = 'website_restaurant_menu_snippet.s_dynamic_restaurant_snippet';
        },

        willStart: function () {
            return this._super.apply(this, arguments).then(
                () => Promise.all([
                    this._fetchData(),
                ])
            );
        },

        start: function () {
            return this._super.apply(this, arguments)
                .then(() => {
                    this._setupSizeChangedManagement(true);
                    this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
                    this._render();
                    this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
                });
        },

        destroy: function () {
            this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerUnactive();
            this._toggleVisibility(false);
            this._setupSizeChangedManagement(false);
            this._clearContent();
            this.options.wysiwyg && this.options.wysiwyg.odooEditor.observerActive();
            this._super.apply(this, arguments);
        },

        _clearContent: function () {
            const $templateArea = this.$el.find('.dynamic_snippet_template');
            this.trigger_up('widgets_stop_request', {
                $target: $templateArea,
            });
            $templateArea.html('');
        },

        _isConfigComplete: function () {
            return this.$el.get(0).dataset.productCategoryId !== undefined && this.$el.get(0).dataset.numberOfRecords !== undefined;
        },

        _getCategorySearchDomain() {
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
                            searchDomain.push(['pos_categ_id.product_tmpl_ids', '=', parseInt(productTemplateId[0].value)]);
                        }
                    }
                }
                if (productCategoryId) {
                    searchDomain.push(['pos_categ_id', 'child_of', parseInt(productCategoryId)]);
                }
            }
            searchDomain.push(['available_in_pos', '=', true])
            searchDomain.push(['available_in_pos', '=', true])
            return searchDomain;
        },

        _getSearchDomain: function () {
            const searchDomain = this._getCategorySearchDomain();
            return searchDomain;
        },

        _getRpcParameters: function () {
            return {};
        },

        async _fetchData() {
            if (this._isConfigComplete()) {
                const nodeData = this.el.dataset;
                console.log(this._getSearchDomain())
                const filterFragments = await this._rpc({
                    'route': '/restaurant/snippet/filters',
                    'params': Object.assign({
                        'filter_id': parseInt(nodeData.filterId),
                        'template_key': nodeData.templateKey,
                        'limit': parseInt(nodeData.numberOfRecords),
                        'search_domain': this._getSearchDomain(),
                        'with_sample': this.editableMode,
                        'context': {
                            '_bugfix_force_minimum_max_limit_to_16': !!nodeData.forceMinimumMaxLimitTo16,
                        },
                    }, this._getRpcParameters()),
                });
                this.data = filterFragments.map(Markup);
            } else {
                this.data = [];
            }
        },

        _prepareContent: function () {
            this.renderedContent = core.qweb.render(
                this.template_key,
                this._getQWebRenderOptions()
            );
        },

         _getQWebRenderOptions: function () {
            const dataset = this.$target[0].dataset;
            const numberOfRecords = parseInt(dataset.numberOfRecords);
            let numberOfElements;
            if (config.device.isMobile) {
                numberOfElements = parseInt(dataset.numberOfElementsSmallDevices) || DEFAULT_NUMBER_OF_ELEMENTS_SM;
            } else {
                numberOfElements = parseInt(dataset.numberOfElements) || DEFAULT_NUMBER_OF_ELEMENTS;
            }
            const chunkSize = numberOfRecords < numberOfElements ? numberOfRecords : numberOfElements;
            return {
                chunkSize: chunkSize,
                data: this.data,
                uniqueId: this.uniqueId,
                extraClasses: dataset.extraClasses || '',
            };
        },

        _render: function () {
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
            if (enable === true) {
                config.device.bus.on('size_changed', this, this._onSizeChanged);
            } else {
                config.device.bus.off('size_changed', this, this._onSizeChanged);
            }
        },

        _toggleVisibility: function (visible) {
            this.$el.toggleClass('o_dynamic_empty', !visible);
        },


        _onSizeChanged: function (size) {
            if (this.isDesplayedAsMobile !== config.device.isMobile) {
                this.isDesplayedAsMobile = config.device.isMobile;
                this._render();
            }
        },
    });

    publicWidget.registry.dynamic_snippet = DynamicSnippet;

    return DynamicSnippet;

});
