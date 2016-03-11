define(['jquery', 'handlebars', 'main', 'text!templates/courses.html', 'text!templates/course_details.html', 'text!templates/error.html'],
    function($, Handlebars, main, tpl, tplDetails, tplError) {
'use strict';
    return {
        render: function() {
            var template = Handlebars.compile(tpl);
            var templateDetails = Handlebars.compile(tplDetails);

            var templateError = Handlebars.compile(tplError);

            main.callCourseseditions(function(data){
                if (data.status == 'success'){
                    $('#page').html(template(data));
                    bindListeners();
                } else {
                    $('#page').html(templateError(data));
                }
            });

            function bindListeners(){
                $('.panel-heading').bind( 'click', function(){
                    //FIXME - do not call when content already loaded
                    var courseId = $(this).attr("course-id");
                    var termId = $(this).attr("term-id");
                    main.callCourseEditionDetails(courseId, termId, function(courseInfo){

                        var idContent = '#courseDetails' + courseId;

                        if (courseInfo.status == 'success'){
                            $(idContent).html(templateDetails(courseInfo.data));
                        } else {
                            $(idContent).html(templateError({'message': courseInfo.message}));
                        }
                    });
              })
            };

        }
    }    
});