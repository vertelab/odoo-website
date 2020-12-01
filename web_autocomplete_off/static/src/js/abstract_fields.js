odoo.define('web_autocomplete_off.AbstractField', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');

    AbstractField.include({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.$el.attr('name', self.name);
                self.$el.addClass('o_field_widget');
                self.$el.each(function (i, el) {
                    if (['INPUT', 'TEXTAREA','SELECT'].some(t => t === el.tagName)
                        && !el.hasAttribute('autocomplete')) {
                        el.setAttribute('autocomplete', 'off');
                    }
                })
                self.$('input, select, textarea')
                    .filter((i, el) => !el.hasAttribute('autocomplete'))
                    .attr('autocomplete', 'off');
                    return self._render();
                });
        },


    });
});
