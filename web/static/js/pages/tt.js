define(['jquery', 'handlebars', 'main', 'nice-select', 'easing', 'bootstrap-table', 'fullcalendar',
'text!templates/tt.html', 'text!templates/error.html', 'fullcalendarpl'], function(
$, Handlebars, main, nice, easing, bootstrapTable, fullcalendar, tpl, tplError, fullcalendarpl) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateError = Handlebars.compile(tplError);

            $('#page-content').html(template());

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

                    main.callTT(start.format(), function(data){
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
                                        type: $(this).attr('type'),
                                    });
                                });
                                callback(events);
                        }
                        else {
                            $('#page-content').html(templateError(data));
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