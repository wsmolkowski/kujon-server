define('navigation', ['jquery', 'handlebars', 'main', 'text!templates/navigation.html'], function($, Handlebars, main, navTpl) {
'use strict';
    return {
        render: function() {

            var navigationTemplate = Handlebars.compile(navTpl);

            main.getConfig(function(config){
                $('#navigation').html(navigationTemplate(config.data));
            });

        }
    }    
});