$(document).ready(function() {

});

function openNav() {
    $("#overlay_nav").css({"height": "100%"});
    $("body").css({"position": "fixed", "overflow": "hidden"});
    $("#oe_main_menu_navbar").css({"display": "none"});
}

function closeNav() {
    $("#overlay_nav").css({"height": "0%"});
    $("body").css({"position": "", "overflow": ""});
    $("#oe_main_menu_navbar").css({"display": ""});
}
