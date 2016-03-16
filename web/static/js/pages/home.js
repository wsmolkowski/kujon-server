define(['jquery', 'handlebars', 'main', 'text!templates/home.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            var data = {
                hello: 'World'              
            };
            
            $('#page').html(template(data));
            
        }
    }    
});