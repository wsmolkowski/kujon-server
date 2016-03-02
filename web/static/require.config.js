// require.js looks for the following global when initializing
var require = {
    baseUrl: ".",
    paths: {
        "bootstrap":            "static/bower_components/bootstrap/dist/js/bootstrap.min",
        "crossroads":           "static/bower_components/crossroads/dist/crossroads.min",
        "hasher":               "static/bower_components/hasher/dist/js/hasher.min",
        "signals":              "static/bower_components/js-signals/dist/signals.min",
        "jquery":               "static/bower_components/jquery/dist/jquery.min",
        "text":                 "static/bower_components/requirejs-text/text",
        "handlebars":           "static/bower_components/handlebars/handlebars.min",
        "jquery-cookie":        "static/bower_components/jquery-cookie/jquery.cookie",
        "fullcalendar":         "static/bower_components/fullcalendar/dist/fullcalendar.min",
        "moment":               "static/bower_components/moment/min/moment.min",
        "templates":            "static/templates",
        "main":                 "static/js/main",
        "navigation":           "static/js/pages/navigation",
        "lib":                  "static/js",
    },
    shim: {
        "bootstrap": { deps: ["jquery"] },
    }
};
