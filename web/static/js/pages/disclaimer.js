define(['jquery', 'handlebars', 'main', 'text!templates/disclaimer.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            var data = {
            };
            
            $('#page').html(template(data));
            
        }
    }    
});