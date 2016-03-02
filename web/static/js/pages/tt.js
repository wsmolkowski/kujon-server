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
                'defaultView': 'agendaWeek',
                'firstDay': 1,
                'aspectRatio': 2,
                'nowIndicator': true,
                events: function(start, end, timezone, callback) {

                        $.ajax({
                            url: 'http://localhost:8881/api/tt/' + start.format('Y-MM-DD'),
                            dataType: 'json',
                            success: function(doc) {
                                var events = [];
                                $(doc).find('data').each(function() {
                                    events.push({
                                        title: $(this).attr('title'),
                                        start: $(this).attr('start') // will be parsed
                                    });
                                });
                                callback(events);
                            }
                        });
                    }
            });

            //a tutaj możesz np. zapiąć listenery, uruchomić subkomponenty jQuery itp.
        }
    }
});