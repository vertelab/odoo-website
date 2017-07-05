$(document).ready(function() {

});

function openNav() {
    $("#overlay_nav").css({"height": "100%"});
    $("body").css({"position": "fixed", "overflow": "hidden"});
}

function closeNav() {
    $("#overlay_nav").css({"height": "0%"});
    $("body").css({"position": "", "overflow": ""});
}
