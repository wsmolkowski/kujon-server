define("main", ["jquery", "handlebars", "text!templates/error.html", 'jquery-cookie'], function($, Handlebars, tplError, jc)
{
        /* variables */
        var templateError = Handlebars.compile(tplError);

        var config;

        function updateConfig(data){
            config = data;
        }

        /* private methods */

        function buildConfig(callback){
            $.ajax({
                    type: 'GET',
                    url: 'http://localhost:8888/config',
                    xhrFields: {
                      withCredentials: true
                    },
                    success:  function (data) {
                      if (data.status == 'success'){
                        updateConfig(data.data);
                        if (callback){
                            callback(data);
                        }
                      } else {
                        $('#page').html(templateError(data));
                      }
                    },
                    error: function(jqXHR, exception) {
                      var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception};
                      $('#page').html(templateError(msg));
                    }
                });
        };

        function getConfig(callback){
            if (! config){
                buildConfig(callback);
            } else {
                callback(config);
            }
        };

        function buildApiUrl(api){
            return config['API_URL'] + api;
        };

        function callAjaxGet(request_url, callback){

            $.ajax({
                type: 'GET',
                url: request_url,
                xhrFields: {
                    withCredentials: true
                },
                beforeSend: function(){
                    $('#spinner').show();
                },
                complete: function(){
                    $('#spinner').hide();
                },
                crossDomain: true,
                success:  function (data) {
                    callback(data);
                },
                error: function(jqXHR, exception) {
                    var msg = {'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception};
                    $('#page').html(templateError(msg));
                }
            });
        };

        function usoses(callback){
            callAjaxGet(buildApiUrl('/api/usoses'), callback);
        };

        function users(callback){
            callAjaxGet(buildApiUrl('/api/users/'), callback);
        };

        function terms(callback){
            callAjaxGet(buildApiUrl('/api/terms/'), callback);
        };

        function programmes(callback){
            callAjaxGet(buildApiUrl('/api/programmes/'), callback);
        };

        function grades(callback){
            callAjaxGet(buildApiUrl('/api/grades/'), callback);
        };

        function courseseditions(callback){
            callAjaxGet(buildApiUrl('/api/courseseditions/'), callback);
        };

        function lecturers(callback){
            callAjaxGet(buildApiUrl('/api/lecturers/'), callback);
        };

        function lecturerDetails(lecturerId, callback){
            var request_url = buildApiUrl('/api/lecturers/') + lecturerId;
            callAjaxGet(request_url, callback);
        };

        function courseDetails(courseId, callback){
            var request_url = buildApiUrl('/api/courses/') + courseId;
            callAjaxGet(request_url, callback);
        };

        function TT(start, callback) {
                var request_url = buildApiUrl('/api/tt/') + start;
                callAjaxGet(request_url, callback);
        };

        /* public methods */
        return {

            init: function() {
                buildConfig(null);

                // {{#nl2br}} replace returns with <br>
                Handlebars.registerHelper('nl2br', function(text) {
                    text = Handlebars.Utils.escapeExpression(text);
                    var nl2br = (text + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + '<br>' + '$2');
                    return new Handlebars.SafeString(nl2br);
                });
            },
            getConfig: function(callback){
                getConfig(callback);
            },
            callUsoses: function(callback){
                usoses(callback);
            },
            callUsers: function(callback){
                users(callback);
            },
            callTerms: function(callback){
                terms(callback);
            },
            callProgrammes: function(callback){
                programmes(callback);
            },
            callGrades: function(callback){
                grades(callback);
            },
            callCourseseditions: function(callback){
                courseseditions(callback);
            },
            callCourseDetails: function(courseId, callback){
                courseDetails(courseId, callback);
            },
            callLecturers: function(callback){
                lecturers(callback);
            },
            callLecturerDetails: function(lecturerId, callback){
                lecturerDetails(lecturerId, callback);
            },
            cleanSecureCookie: function(){
                $.cookie(config['USER_SECURE_COOKIE'], null);
            },
            isUserLoggedIn: function(){
                if (! $.cookie('USER_SECURE_COOKIE')){
                    return false;
                } else {
                    return true;
                }
            },
            callTT: function(start, callback){
                TT(start, callback);
            },


        };

});
