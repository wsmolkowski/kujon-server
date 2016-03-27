define(['jquery', 'handlebars', 'main', 'text!templates/terms.html', 'text!templates/error.html', 'datatables'],
function($, Handlebars, main, tpl, tplError, datatables) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            main.callTerms(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }

                $('#terms-table').DataTable(main.getDatableConfig());

            });
            
            //a tutaj możesz np. zapiąć listenery
        }
    }    
});