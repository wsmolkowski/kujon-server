define(['jquery', 'handlebars', 'text!templates/contact.html'],
function($, Handlebars, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            $('#page-content').html(template());
        }
    }
});