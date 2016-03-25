// require.js looks for the following global when initializing
var require = {
    baseUrl: ".",
    paths: {
        "jquery":               "static/bower_components/jquery/dist/jquery.min",
        "bootstrap":            "static/bower_components/bootstrap/dist/js/bootstrap.min",
        "crossroads":           "static/bower_components/crossroads/dist/crossroads.min",
        "hasher":               "static/bower_components/hasher/dist/js/hasher.min",
        "signals":              "static/bower_components/js-signals/dist/signals.min",
        "text":                 "static/bower_components/text/text",
        "handlebars":           "static/bower_components/handlebars/handlebars.min",
        "moment":               "static/bower_components/moment/min/moment.min",
        "jquery-cookie":        "static/bower_components/jquery.cookie/jquery.cookie",
        "fullcalendar":         "static/bower_components/fullcalendar/dist/fullcalendar.min",
        "fullcalendarpl":       "static/bower_components/fullcalendar/dist/lang/pl",
        "datatables":           "static/bower_components/datatables/media/js/jquery.dataTables.min",
        "templates":            "static/templates",
        "main":                 "static/js/main",
        "navigation":           "static/js/pages/navigation",
        "lib":                  "static/js",
    },
    shim: {
        "bootstrap": { deps: ["jquery"] },
        "fullcalendarpl": { deps: ["fullcalendar"] },
    }
};
