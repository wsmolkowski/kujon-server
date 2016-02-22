define(['jquery', 'handlebars', 'main', 'text!templates/lecturers.html', 'text!templates/lecturer_details.html', 'text!templates/error.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);

            var templateError = Handlebars.compile(tplError);

            var request_url = main.getApiUrl('/api/lecturers/');

            $.ajax({
                type: 'GET',
                url: request_url,
                xhrFields: {
                    withCredentials: true
                },
                crossDomain: true,
                success:  function (data) {
                    if (data.status == 'success'){
                        $('#page').html(template(data));

                        bindListeners();

                    } else {
                        $('#page').html(templateError(data));
                    }
                },
                error: function(jqXHR, exception) {
                    var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.responseText + ' exception: ' + exception};
                    $('#page').html(templateError(msg));
                }
            });

            function bindListeners(){

                $('.panel-heading').bind( 'click', function(){
                    //FIXME - do not call when content already loaded
                    var lecturerId = $(this).attr("lecturer-id");
                    main.callLecturerDetails(lecturerId, function(lecturerInfo){

                        var idContent = '#lecturerDetails' + lecturerId;

                        if (lecturerInfo.status == 'success'){
                            $(idContent).html(templateDetails(lecturerInfo.data));
                        } else {
                            $(idContent).html(templateError(lecturerInfo));
                        }
                    });
              })
            };

        }
    }    
});