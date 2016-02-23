define(['jquery', 'handlebars', 'main', 'text!templates/home.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var config = main.getConfig();
            var template = Handlebars.compile(tpl);



            //tutaj możesz zrobić np. wywołanie JSON
            
            var data = {
                hello: 'World'              
            };
            
            $('#page').html(template(data));
            
            //a tutaj możesz np. zapiąć listenery, uruchomić subkomponenty jQuery itp.
        }
    }    
});