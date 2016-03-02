define(['jquery', 'handlebars', 'main', 'fullcalendar', 'text!templates/tt.html'], function($, Handlebars, main, fullcalendar, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            //tutaj możesz zrobić np. wywołanie JSON

            var data = {
                hello: 'World'
            };

            $('#page').html(template(data));

            $('#calendar').fullCalendar({
                // put your options and callbacks here

            });
            //a tutaj możesz np. zapiąć listenery, uruchomić subkomponenty jQuery itp.
        }
    }    
});