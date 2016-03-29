define(['jquery', 'handlebars', 'main', 'text!templates/index.html'], function($, Handlebars, main, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            $.when(main.init()).then(function(){
                var config = main.getConfig();
                $('#page').html(template(config));
            });

            main.callUsoses(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }
            });

        }
    }    
});