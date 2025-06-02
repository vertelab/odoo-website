/** @odoo-module **/
import options from '@web_editor/js/editor/snippets.options';
//import core from 'web.core';
import { rpc } from "@web/core/network/rpc";
import s_dynamic_snippet_carousel_options from "@website/snippets/s_dynamic_snippet_carousel/options";
import wUtils from "@website/js/utils";



const dynamicRestaurantMenuSnippetOptions = options.Class.extend({

     init: function () {
        console.log("options.js: init")
        this._super.apply(this, arguments);
        this.modelNameFilter = 'pos.category';
        this.posCategories = {};
        this.selectedCategories = new Set();
        this.categoryContainer = null;
        
        this.isOptionDefault = {};
    },

    async onBuilt() {
        console.log("options.js: onBuilt")
        await this._super.apply(this, arguments);

//        this.$target[0].dataset['snippet'] = 's_dynamic_snippet_restaurant_menu';

        if (this._isNewSnippet()) {
            await this._setOptionsDefaultValues();
        }
//        const classList = [...this.$target[0].classList];
//        if (classList.includes('d-none') && !classList.some(className => className.match(/^d-(md|lg)-(?!none)/))) {
//            // Remove the 'd-none' of the old template if it is not related to
//            // the visible on mobile option.
//            this.$target[0].classList.remove('d-none');
//        }
        return this._refreshPublicWidgets();
    },
    
    /** 
     * @private
     * @returns {boolean}
     */
     
     _isNewSnippet: function() {
        const dataset = this.$target[0].dataset;
        return !dataset.posCategoryId && !dataset.templateKey;
    },    

    async _setOptionsDefaultValues() {
        console.log("options.js: _setOptionsDefaultValues")
        this.options.wysiwyg.odooEditor.observerUnactive();
        
        if (!this.$target[0].dataset.filterId) {
            this._setOptionValue('filterId', this.$target[0].dataset.filterId || 
                document.querySelector('[data-filter-id]')?.dataset.filterId);
        }
        if (!this.$target[0].dataset.templateKey) {
            this._setOptionValue('templateKey', 'dynamic_filter_template_pos_category_restaurant_menu_1');
        }
        if (!this.$target[0].dataset.numberOfRecords) {
            this._setOptionValue('numberOfRecords', '16');
        }
        if (!this.$target[0].dataset.posCategoryIds) {
            this._setOptionValue('posCategoryIds', 'all');
        }
        
        this.options.wysiwyg.odooEditor.observerActive();
    },

    _fetchPosCategories: function () {
        console.log("options.js: _fetchPosCategories")
        return this.orm.searchRead("pos.category", 
            [...wUtils.websiteDomain(this), ['available_in_menu', '=', true]], 
            ["id", "name"]);
    },
    /**
     *
     * @override
     * @private
     */
    _renderCustomXML: async function (uiFragment) {
        console.log("options.js: _renderCustomXML")
        await this._super.apply(this, arguments);
        await this._renderPosCategorySelector(uiFragment);
    },
    /**
     * Renders the product categories option selector content into the provided uiFragment.
     * @private
     * @param {HTMLElement} uiFragment
     */
    _renderPosCategorySelector: async function (uiFragment) {
        console.log("options.js: _renderPosCategorySelector")
        const publishedPosCategories = await this._fetchPosCategories();

        for (let index in publishedPosCategories) {
            this.posCategories[publishedPosCategories[index].id] = publishedPosCategories[index];
        }
        
        const posCategoriesSelectorEl = uiFragment.querySelector('[data-name="pos_category_opt"]');
        if (posCategoriesSelectorEl) {
            posCategoriesSelectorEl.innerHTML = '';
            
            this.categoryContainer = document.createElement('div');
            this.categoryContainer.className = 'o_we_category_selector d-flex flex-wrap gap-2 mb-2 w-100';

            const allWrapper = this._createCategoryOption('all', 'All Categories', true);
            this.categoryContainer.appendChild(allWrapper);

            for (let id in this.posCategories) {
                const categoryWrapper = this._createCategoryOption(id, this.posCategories[id].name, false);
                this.categoryContainer.appendChild(categoryWrapper);
            }
            posCategoriesSelectorEl.appendChild(this.categoryContainer);
            
            this._parseExistingSelection();
            this._updateCategoryCheckboxStates();
        }
    },


    _createCategoryOption: function(categoryId, categoryName, isAllOption = false) {
        console.log("options.js: _createCategoryOption");
        const wrapper = document.createElement('div');
        wrapper.className = 'form-check d-flex align-items-center mb-2 w-100';
        wrapper.dataset.categoryId = categoryId;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `category_${categoryId}`;
        checkbox.className = 'form-check-input me-2';
        checkbox.dataset.categoryId = categoryId;

        const label = document.createElement('label');
        label.htmlFor = `category_${categoryId}`;
        label.className = 'form-check-label mb-0 small flex-grow-1';
        label.textContent = categoryName;

        if (isAllOption) {
            label.className += ' fw-bold';
            wrapper.className += ' border-bottom pb-2 mb-3';
        }
        checkbox.addEventListener('change', (e) => {
            this._handleCategorySelection(categoryId, e.target.checked);
        });
        wrapper.appendChild(checkbox);
        wrapper.appendChild(label);
        return wrapper;
    },

    _handleCategorySelection: function(categoryId, isChecked) {
        console.log("options.js: _handleCategorySelection");
        if (categoryId === 'all') {
            if (isChecked) {
                this.selectedCategories.clear();
                this.selectedCategories.add('all');
                this._uncheckAllIndividualCategories();
            } else {
                this.selectedCategories.delete('all');
                if (this.selectedCategories.size === 0) {
                    this.selectedCategories.add('all');
                    this._checkAllOption();
                }
            }
        } else {
            if (this.selectedCategories.has('all')) {
                this.selectedCategories.delete('all');
                this._uncheckAllOption();
            }
            
            if (isChecked) {
                this.selectedCategories.add(categoryId);
            } else {
                this.selectedCategories.delete(categoryId);
            }

            if (this.selectedCategories.size === 0) {
                this.selectedCategories.add('all');
                this._checkAllOption();
            }
        }
        this._updateDataAttribute();
        this._refreshPublicWidgets();
    },

    _uncheckAllIndividualCategories: function() {
        console.log("options.js: _uncheckAllIndividualCategories");
        const checkboxes = this.categoryContainer.querySelectorAll('input[type="checkbox"]:not([data-category-id="all"])');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    },

    _checkAllOption: function() {
        console.log("options.js: _checkAllOption");
        const allCheckbox = this.categoryContainer.querySelector('input[data-category-id="all"]');
        if (allCheckbox) {
            allCheckbox.checked = true;
        }
    },

    _uncheckAllOption: function() {        
        console.log("options.js: _unchecbAllOptions");
        const allCheckbox = this.categoryContainer.querySelector('input[data-category-id="all"]');
        if (allCheckbox) {
            allCheckbox.checked = false;
        }
    },
    
    _updateCategoryCheckboxStates: function() {
        console.log("options.js: _updateCategoryCheckboxStates");
        const checkboxes = this.categoryContainer.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            const categoryId = checkbox.dataset.categoryId;
            checkbox.checked = this.selectedCategories.has(categoryId);
        });
    },
    
    _updateDataAttribute: function() {
        console.log("options.js: _updateDataAttribute");
        const selectedArray = Array.from(this.selectedCategories);
        const dataValue = selectedArray.length === 1 && selectedArray[0] === 'all' 
            ? 'all' 
            : selectedArray.filter(id => id !== 'all').join(',');
        
        this._setOptionValue('posCategoryIds', dataValue);
    },

    _parseExistingSelection: function() {
        console.log("options.js: _parseExsistingSelection");
        const currentValue = this.$target[0].dataset.posCategoryIds || 'all';
        
        this.selectedCategories.clear();
        
        if (currentValue === 'all' || !currentValue) {
            this.selectedCategories.add('all');
        } else {
            const categoryIds = currentValue.split(',').filter(id => id.trim());
            categoryIds.forEach(id => this.selectedCategories.add(id.trim()));

            if (this.selectedCategories.size === 0) {
                this.selectedCategories.add('all');
            }
        }
    },

    _setOptionValue: function (optionName, value) {
        console.log("options.js: _setOptionValue")
        this.$target.get(0).dataset[optionName] = value;
    },
    
    async onTemplateKey(templateKey) {
        console.log("options.js: onTemplateKey");
        this.$target.get(0).dataset.templateKey = templateKey;
        await this._refreshPublicWidgets();
    },
    
    async onNumberOfRecords(numberOfRecords) {
        console.log("options.js: onNumberOfRecords");
        this.$target.get(0).dataset.numberOfRecords = numberOfRecords;
        await this._refreshPublicWidgets();
    },
    
    start: function () {
        console.log("options.js: start");
        this._parseExistingSelection();
        return this._super.apply(this, arguments);
    }
})

options.registry.dynamic_restaurant_menu_snippet = dynamicRestaurantMenuSnippetOptions;

return dynamicRestaurantMenuSnippetOptions;
