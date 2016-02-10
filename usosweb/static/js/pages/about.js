define(['jquery', 'handlebars', 'text!templates/about.html'], function($, Handlebars, tpl) {
'use strict';
    return {
        render: function() {
        
            var template = Handlebars.compile(tpl);
            
            //tutaj możesz zrobić np. wywołanie JSON
            
            var data = {
                hello: 'About'              
            };
            
            $('#page').html(template(data));           
            
            //a tutaj możesz np. zapiąć listenery
        }
    }    
});