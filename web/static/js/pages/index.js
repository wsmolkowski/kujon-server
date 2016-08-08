define(['jquery', 'handlebars', 'main', 'text!templates/index.html', 'text!templates/error.html'],
function($, Handlebars, main, tpl, tplError) {
    'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.ajaxGet('/config').then(function(data) {
                if (data.status == 'success') {
                    $('#section-content').html(template(data.data));
                } else {
                    $('#section-content').html(templateError({
                        'message': data.message
                    }));
                }
            });
        }
    }
});
