var divider = $("#top_menu").find(".divider").closest("li");
var my_account = $("#top_menu").find(".dropdown-menu.js_usermenu").closest("li");
var more_menu = $("#top_menu").find("li#more_dropdown");
var menu_items = [];
var more_menu_items = [];
$("#top_menu").children().each(function() {
    if($(this).attr("class") == "divider")
        return false;
    else
        menu_items.push($(this));
});
$("#top_menu").find("#more_dropdown").find("ul").children().each(function() {
    more_menu_items.push($(this));
});

var li_width_init = divider.width() + my_account.width() + 40; // extra pixels to avoid change row
if(menu_items.length == 0) {
    more_menu.css({"display": "none"});
}
else if(menu_items.length != 0) {
    li_width_init += more_menu.width();
}

$(document).ready(function() {
    if($(window).width() > 758) {
        var max_li_width = $("#top_menu").width() - li_width_init;
        var li_width = 0;
        $.each(menu_items, function(index) {
            li_width += $(this).width();
            if (li_width > max_li_width) {
                $(this).css({"display": "none"});
            }
            else {
                more_menu_items[index].css({"display": "none"});
            }
        });
    }
});

$(window).resize(function() {
    if($(window).width() > 758) {
        var max_li_width = $("#top_menu").width() - li_width_init;
        var li_width = 0;
        $.each(menu_items, function(index) {
            li_width += $(this).width();
            if (li_width > max_li_width) {
                $(this).css({"display": "none"});
                more_menu_items[index].css({"display": "inline"});
            }
            else {
                $(this).css({"display": "inline"});
                more_menu_items[index].css({"display": "none"});
            }
        });
    }
});
