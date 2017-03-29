$(document).ready(function() {
    $('.oe_select2_search').select2();
    $('.oe_select9_search').select9();
    $("select.oe_select9_search_field").select9({
        tags: true
    });
    
    $("select.oe_select9_search_field").on("select9:select", function (evt) {
        value = "";
        $(this).children("option:selected").each(function (index, element) {
            value = value + " " + element.value
        });
        $(this).closest("form").find(".oe_select9_search_input").val(value)
        $(this).closest("form").submit();
    });
    
    $("select.oe_select9_search_field").on("select9:unselect", function (evt) {
        value = "";
        $(this).children("option:selected").each(function (index, element) {
            value = value + " " + element.value
        });
        $(this).closest("form").find(".oe_select9_search_input").val(value)
    });
    
    //~ $("form.oe_select9_search_form").submit(function (evt) {
        //~ value = "";
        //~ $(this).find(".oe_select9_search_input").children("option").each(function (index, element) {
            //~ value = value + " " + element.value
        //~ });
        //~ $(this).find(".oe_select9_search_input").val(value)
    //~ });
});
