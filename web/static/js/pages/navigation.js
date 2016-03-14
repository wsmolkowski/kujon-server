define('navigation', ['jquery', 'handlebars', 'main', 'text!templates/navigation.html'], function($, Handlebars, main, navTpl) {
'use strict';
    return {
        render: function() {

            var navigationTemplate = Handlebars.compile(navTpl);

            main.getConfig(function(config){
                $('#navigation').html(navigationTemplate(config.data));

                //a tutaj możesz np. zapiąć listenery, uruchomić subkomponenty jQuery itp.
                $('.login-button').click(function(){
                    main.showSpinner();
                    return true;
                });

            });
        }
    }    
});