define('navigation', ['jquery', 'handlebars', 'main', 'text!templates/navigation.html'], function($, Handlebars, main, navTpl) {
'use strict';
    return {
        render: function() {

            var navigationTemplate = Handlebars.compile(navTpl);

            main.getConfig(function(data){
                $('#navigation').html(navigationTemplate(data.data));
            });

            //tutaj możesz zrobić np. wywołanie JSON
            
            //a tutaj możesz np. zapiąć listenery, uruchomić subkomponenty jQuery itp.
        }
    }    
});