define(['jquery', 'handlebars', 'main', 'text!templates/lecturers.html', 'text!templates/lecturer_details.html', 'text!templates/error.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError) {
    'use strict';

    return {
        render: function() {

            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);

            var templateError = Handlebars.compile(tplError);

            main.callLecturers(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                    bindListeners();
                } else {
                    $('#page').html(templateError({'message': data.message}));
                }
            });

            var API_URL;

            main.getConfig(function(config){
                API_URL = config['API_URL'];
            });

            function bindListeners(){
                $('a.panel-row').bind( 'click', function(){
                    var lecturerId = $(this).attr("lecturer-id");
                    var ariaexpanded = $(this).attr("aria-expanded");
                    if (ariaexpanded == "false") {
                        $(this).attr("aria-expanded","true");
                        main.callLecturerDetails(lecturerId, function(lecturerInfo){
                            var idContent = '#lecturerDetails' + lecturerId;

                            if (lecturerInfo.status == 'success'){
                                lecturerInfo.data['API_URL'] = API_URL;
                                $(idContent).html(templateDetails(lecturerInfo.data));
                            } else {
                                $(idContent).html(templateError({'message': lecturerInfo.message}));
                            }
                        });
                    } else {
                        $(this).attr("aria-expanded","false");
                    }
                })
            };

        }
    }    
});