define(['jquery', 'handlebars', 'main', 'text!templates/index.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            $('#section-content').html(template());

        }
    }    
});