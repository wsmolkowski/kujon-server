define('navigation', ['jquery', 'handlebars', 'main', 'text!templates/navigation.html'], function($, Handlebars, main, navTpl) {
'use strict';
    return {
        render: function() {

            var navigationTemplate = Handlebars.compile(navTpl);

            $.when(main.init()).then(function(){
                var config = main.getConfig();
                $('#navigation').html(navigationTemplate(config));

                //a tutaj możesz np. zapiąć listenery, uruchomić subkomponenty jQuery itp.
                $('.login-button').click(function(){
                    main.showSpinner();
                    return true;
                });
            });
        }
    }    
});