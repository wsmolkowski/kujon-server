define(['jquery', 'handlebars', 'main', 'nice-select', 'easing', 'bootstrap-table', 'text!templates/faculties.html', 'text!templates/error.html'],
function($, Handlebars, main, nice, easing, bootstrapTable, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callFaculties(function(data){
                if (data.status == 'success'){
                    $('#page-content').html(template(data));
                } else {
                    $('#page-content').html(templateError({'message': data.message}));
                }
            });
        }
    }    
});