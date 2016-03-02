define(['jquery', 'handlebars', 'main', 'text!templates/login.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {

            $('#page').html(Handlebars.compile(tpl));
            
            //a tutaj możesz np. zapiąć listenery, uruchomić subkomponenty jQuery itp.
        }
    }    
});