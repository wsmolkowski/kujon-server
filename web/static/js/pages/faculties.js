define(['jquery', 'handlebars', 'main', 'text!templates/faculties.html', 'text!templates/error.html', 'datatables'],
function($, Handlebars, main, tpl, tplError, datatables) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callFaculties(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }

                $('#faculties-table').DataTable(main.getDatableConfig());

            });
        }
    }    
});