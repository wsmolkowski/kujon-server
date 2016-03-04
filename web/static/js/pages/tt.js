define(['jquery', 'handlebars', 'main', 'fullcalendar', 'text!templates/tt.html', 'text!templates/error.html', 'fullcalendarpl'], function($, Handlebars, main, fullcalendar, tpl, tplError, fullcalendarpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            $('#page').html(template());

            $('#calendar').fullCalendar({
                'defaultView': 'agendaWeek',
                'firstDay': 1,
                lang: 'pl',
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
                                        title: $(this).attr('title'),// will be parsed
                                        start: $(this).attr('start_date'),
                                        end: $(this).attr('end_date'),
                                        room_number: $(this).attr('room_number'),
                                        building_name: $(this).attr('building_name'),
                                        group_number: $(this).attr('group_number'),
                                        type: $(this).attr('type'),
                                    });
                                });
                                callback(events);
                        }
                        else {
                            $('#page').html(templateError(data));
                        }
                    });
                },
                'timeFormat': 'H:mm',
                'axisFormat': 'H:mm',
                'columnFormat': 'ddd DD/MM',
                'eventRender': function(event, element) {
                    var description = "sala: " + event.room_number + "<br>"
                    description += "budynek: " + event.building_name + "<br>"
                    description += "grupa: " + event.group_number + "<br>"
                    description += "typ: " + event.type
                    element.tooltip({title: description, html: true, container: "body", placement: 'right'});
                }
            });
        }
    }
});