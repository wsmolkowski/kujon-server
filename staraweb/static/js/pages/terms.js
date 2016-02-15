define(['jquery', 'handlebars', 'main', 'text!templates/user.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
        
            var template = Handlebars.compile(tpl);
            
            //tutaj możesz zrobić np. wywołanie JSON
            
            var data = {
                hello: 'Terms'
            };
            
            $('#page').html(template(data));           
            
            //a tutaj możesz np. zapiąć listenery
        }
    }    
});