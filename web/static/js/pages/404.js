define(['jquery', 'handlebars', 'main', 'text!templates/404.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            $('#page').html(template());
        }
    }    
});