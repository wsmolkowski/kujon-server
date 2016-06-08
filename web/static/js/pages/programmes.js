define(['jquery', 'handlebars', 'main', 'text!templates/programmes.html', 'text!templates/error.html'],
function($, Handlebars, main, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callProgrammes(function(data){
                if (data.status == 'success'){
                    $('#section-content').html(template(data));
                    $('#table-programmes').DataTable(main.getDataTableConfig());
                } else {
                    $('#section-content').html(templateError({'message': data.message}));
                }
            });

        }
    }    
});