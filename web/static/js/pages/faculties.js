define(['jquery', 'handlebars', 'main', 'text!templates/faculties.html', 'text!templates/error.html'],
function($, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.ajaxGet('/faculties').then(function(data){
                if (data.status == 'success'){
                    $('#section-content').html(template(data));
                    $('#table-faculties').DataTable(main.getDataTableConfig());
                } else {
                    $('#section-content').html(templateError({'message': data.message}));
                }
            });
        }
    }
});
