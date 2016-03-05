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

            function bindListeners(){
                $('.panel-heading').bind( 'click', function(){
                    //FIXME - do not call when content already loaded

                    var lecturerId = $(this).attr("lecturer-id");

                    main.callLecturerDetails(lecturerId, function(lecturerInfo){
                        var idContent = '#lecturerDetails' + lecturerId;
                        var API_URL;

                        main.getConfig(function(config){
                            API_URL = config['API_URL'];
                        });

                        if (lecturerInfo.status == 'success'){
                            lecturerInfo.data['API_URL']=API_URL;
                            $(idContent).html(templateDetails(lecturerInfo.data));
                        } else {
                            $(idContent).html(templateError({'message': lecturerInfo.message}));
                        }
                    });


                })
            };

        }
    }    
});