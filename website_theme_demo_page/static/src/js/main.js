$(document).ready(function() {
    $("#device_width").append($(window).width());
    $("#device_height").append($(window).height());
});

$(window).resize(function() {
    $("#device_width").html($(window).width());
    $("#device_height").html($(window).height());
});
