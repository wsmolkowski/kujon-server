define(['jquery', 'handlebars', 'main', 'fullcalendar', 'text!templates/tt.html'], function($, Handlebars, main, fullcalendar, tpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);

            var data = {
                hello: 'World'
            };

            $('#page').html(template(data));

            $('#calendar').fullCalendar({
                'defaultView': 'agendaWeek',
                'firstDay': 1,
                'aspectRatio': 2,
                'nowIndicator': true,
                'lang': 'pl',
                'minTime': '07:00',
                'maxTime': '21:00',
                events: function(start, end, timezone, callback) {

                        $.ajax({
                            url: 'http://localhost:8881/api/tt/' + start.format('Y-MM-DD'),
                            dataType: 'json',
                            xhrFields: {
                                withCredentials: true
                            },
                            success: function(doc) {
                                var events = [];
                                $(doc.data).each(function() {
                                    events.push({
                                        title: $(this).attr('title'),
                                        start: $(this).attr('start_date') // will be parsed
                                    });
                                });
                                callback(events);
                            }
                        });
                    }
            });
        }
    }
});