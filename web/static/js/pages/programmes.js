define(['jquery', 'handlebars', 'main', 'nice-select', 'easing', 'bootstrap-table', 'text!templates/programmes.html', 'text!templates/error.html'],
function($, Handlebars, main, nice, easing, bootstrapTable, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callProgrammes(function(data){
                if (data.status == 'success'){
                    $('#section-content').html(template(data));
                } else {
                    $('#section-content').html(templateError({'message': data.message}));
                }
            });

        }
    }    
});