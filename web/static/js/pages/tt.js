define(['jquery', 'handlebars', 'main', 'fullcalendar',
'text!templates/tt.html', 'text!templates/error.html', 'fullcalendarpl'], function(
$, Handlebars, main, fullcalendar, tpl, tplError, fullcalendarpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            $('#section-content').html(template());

            $('#calendar').fullCalendar({
                'defaultView': 'agendaWeek',
                'firstDay': 1,
                'lang': 'pl',
                'aspectRatio': 2,
                'nowIndicator': true,
                'lang': 'pl',
                'minTime': '07:00',
                'maxTime': '21:00',
                events: function(start, end, timezone, callback) {

                    main.ajaxGet('/tt/' + start.format() + '?lecturers_info=False').then(function(data){
                        if (data.status == 'success'){
                                var events = [];
                                $(data.data).each(function() {
                                    events.push({
                                        title: $(this).attr('name'),
                                        start: $(this).attr('start_time'),
                                        end: $(this).attr('end_time'),
                                        room_number: $(this).attr('room_number'),
                                        building_name: $(this).attr('building_name'),
                                        group_number: $(this).attr('group_number'),
                                        lecturer: $(this).attr('lecturers'),
                                        type: $(this).attr('type'),
                                    });
                                });
                                callback(events);
                        }
                        else {
                            $('#section-content').html(templateError(data));
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
                    description += "typ: " + event.type + "<br>"

                    if (event.lecturer.length > 0){
                        description += "prowadzący: " + event.lecturer[0].first_name + " " + event.lecturer[0].last_name
                    }
                    element.tooltip({title: description, html: true, container: "body", placement: 'right'});
                }
            });
        }
    }
});