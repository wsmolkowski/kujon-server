
define("main", ["jquery", "handlebars", "text!templates/error.html"], function($, Handlebars, tplError) {
        var templateError = Handlebars.compile(tplError);

        var config;

        function updateConfig(data){
            config = data;
        };

        function buildConfig(){
            $.ajax({
                    type: 'GET',
                    url: 'http://localhost:8888/config',
                    async: false,
                    success:  function (data) {
                        updateConfig(data);
                    },
                    error: function (err) {

                        console.log(err);
                    }
                });
        };

        function buildApiUrl(api){
            if (!config){
                buildConfig();
            };

            return config['USOS_API'] + api;
        };

        function callAjaxGet(request_url, callback){

            $.ajax({
                type: 'GET',
                url: request_url,
                xhrFields: {
                    withCredentials: true
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
            callUsers(buildApiUrl('/api/usoses/'), callback);
        };

        function terms(callback){
            callUsers(buildApiUrl('/api/users/'), callback);
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

        return {
            getConfig: function() {
                if (!config){
                    buildConfig();
                }
                return config;
            },
            getApiUrl: function(api) {
                if (!config){
                    buildConfig();
                }
                return config['USOS_API'] + api;
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
            callLecturers: function(callback){
                lecturers(callback);
            },
            callLecturerDetails: function(lecturerId, callback){
                lecturerDetails(lecturerId, callback);
            }
        };


});
