$(document).ready(function(){

    openerp.jsonRpc("/website_sale_update_cart", "call", {
    }).done(function(data){
        $(".oe_currency_value").html(data['amount_total']);
        $(".my_cart_quantity").html('(' + data['cart_quantity'] + ')');
    });

});
