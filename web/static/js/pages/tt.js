define(['jquery', 'handlebars', 'main', 'fullcalendar', 'text!templates/tt.html', 'text!templates/error.html'], function($, Handlebars, main, fullcalendar, tpl, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            $('#page').html(template());

            $('#calendar').fullCalendar({
                'defaultView': 'agendaWeek',
                'firstDay': 1,
                'aspectRatio': 2,
                'nowIndicator': true,
                'lang': 'pl',
                'minTime': '07:00',
                'maxTime': '21:00',
                events: function(start, end, timezone, callback) {

                    main.callTT(start, function(data){
                        if (data.status == 'success'){
                                var events = [];
                                $(data.data).each(function() {
                                    events.push({
                                        title: $(this).attr('title'),
                                        start: $(this).attr('start_date') // will be parsed
                                    });
                                });
                                callback(events);
                        }
                        else {
                            $('#page').html(templateError(data));
                        }
                    });
                }
            });
        }
    }
});