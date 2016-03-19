define("main", ["jquery", "handlebars", "text!templates/error.html", 'jquery-cookie'], function($, Handlebars, tplError, jc)
{
        /* variables */
        var templateError = Handlebars.compile(tplError);
        var config;


        function updateConfig(data){
            config = data;
        }

        var spinner = 0;

        /* private methods */

        function showSpinner(){
            if (spinner < 1){
                $('#spinner').show();
                spinner ++;
            }
        }

        function hideSpinner(){
            if (spinner > 0){
                $('#spinner').hide();
                spinner = spinner - 1;
            }
        }

        function buildConfig(){
            return $.ajax({
                    type: 'GET',
                    url: 'http://localhost:8888/config',
                    xhrFields: {
                      withCredentials: true
                    },
                    success:  function (data) {
                      if (data.status == 'success'){
                        updateConfig(data.data);

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

        function buildApiUrl(api){
            return config['API_URL'] + api;
        };

        function buildWebUrl(url){
            return config['DEPLOY_URL'] + url;
        };

        function callAjaxPost(request_url, jsonData, callback){

            $.ajax({
                type: 'POST',
                url: request_url,
                data: JSON.stringify(jsonData),
                contentType: "application/json",
                dataType: "json",
                xhrFields: {
                    withCredentials: true
                },
                beforeSend: function(){
                    showSpinner();
                },
                complete: function(){
                    hideSpinner();
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

        function callAjaxGet(request_url, callback){

            $.ajax({
                type: 'GET',
                url: request_url,
                xhrFields: {
                    withCredentials: true
                },
                beforeSend: function(){
                    showSpinner();
                },
                complete: function(){
                    hideSpinner();
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

        function userInfo(userId, callback){
            var request_url = buildApiUrl('/api/users/') + userId;
            callAjaxGet(request_url, callback);
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

        function courseEditionDetails(courseId, termId, callback){
            var request_url = buildApiUrl('/api/courseseditions/') + courseId + '/' + encodeURIComponent(termId);
            callAjaxGet(request_url, callback);
        };

        function TT(start, callback) {
            var request_url = buildApiUrl('/api/tt/') + start;
            callAjaxGet(request_url, callback);
        };

        function registerUsos(usosId){
            var url = buildWebUrl('/authentication/register');
            var data = {
                'usos_id': usosId
            }

            callAjaxPost(url, data, function(response){
                if (response.status == 'success' && response.data.redirect !== undefined){
                    window.location.href = response.data.redirect;
                } else {
                    $('#page').html(templateError(response));
                }
            });
        }

        /* public methods */
        return {

            init: function() {

                // {{#nl2br}} replace returns with <br>
                Handlebars.registerHelper('nl2br', function(text) {
                    text = Handlebars.Utils.escapeExpression(text);
                    var nl2br = (text + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + '<br>' + '$2');
                    return new Handlebars.SafeString(nl2br);
                });

                // {{#replace}} replace string handlebar helper
                 Handlebars.registerHelper('replacebrackets', function( string ){
	                var pom= ( string || '' ).replace( "(", "\\(" );
	                pom = ( pom || '' ).replace( ")", "\\)" );
	                return pom;
                });

                return buildConfig();
            },
            getConfig: function(){
                return config;
            },
            callUsoses: function(callback){
                usoses(callback);
            },
            callUsers: function(callback){
                users(callback);
            },
            callUserInfo: function(userId, callback){
                userInfo(userId, callback);
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
            callCourseEditionDetails: function(courseId, termId, callback){
                courseEditionDetails(courseId, termId, callback);
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
            isUserRegistered: function(){
                return config['USOS_PAIRED'];
            },
            callTT: function(start, callback){
                TT(start, callback);
            },
            showSpinner: function(){
                showSpinner();
            },
            hideSpinner: function(){
                hideSpinner();
            },
            callRegisterUsos: function(usosId){
                registerUsos(usosId);
            }
        };

});
