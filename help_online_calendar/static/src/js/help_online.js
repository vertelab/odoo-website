openerp.help_online_calendar = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var _lt = instance.web._lt;
    
    instance.web_calendar.CalendarView.include({
        view_loading: function(r) {
            var ret = this._super(r);
            if(! _.isUndefined(this.ViewManager.load_help_buttons)){
                this.ViewManager.load_help_buttons();
            }
            return ret
        },
    });
};
