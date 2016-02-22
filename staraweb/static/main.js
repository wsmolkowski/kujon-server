
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

        function lecturerDetails(lecturerId, callback){
            var request_url = buildApiUrl('/api/lecturers/') + lecturerId;
            callAjaxGet(request_url, callback);
        };

        function lecturers(callback){
            callAjaxGet(buildApiUrl('/api/lecturers/'), callback);
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
            callLecturers: function(callback){
                lecturers(callback);
            },
            callLecturerDetails: function(lecturerId, callback){
                lecturerDetails(lecturerId, callback);
            }
        };


});
