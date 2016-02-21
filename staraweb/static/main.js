
define("main", ["jquery", ], function($) {

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
                var url = config['USOS_API'] + api;
                return url;
            }
        };


});
