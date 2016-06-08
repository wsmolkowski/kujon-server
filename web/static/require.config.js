// require.js looks for the following global when initializing
var require = {
    baseUrl: ".",
    paths: {
        "jquery":               "/static/bower_components/jquery/dist/jquery.min",
        "bootstrap":            "/static/bower_components/bootstrap/dist/js/bootstrap.min",
        "crossroads":           "/static/bower_components/crossroads/dist/crossroads.min",
        "hasher":               "/static/bower_components/hasher/dist/js/hasher.min",
        "signals":              "/static/bower_components/js-signals/dist/signals.min",
        "text":                 "/static/bower_components/text/text",
        "handlebars":           "/static/bower_components/handlebars/handlebars.min",
        "moment":               "/static/bower_components/moment/min/moment.min",
        "jquery-cookie":        "/static/bower_components/jquery.cookie/jquery.cookie",
        "fullcalendar":         "/static/bower_components/fullcalendar/dist/fullcalendar.min",
        "fullcalendarpl":       "/static/bower_components/fullcalendar/dist/lang/pl",
        "cookiebar":            "/static/bower_components/cookiebar/dist/cookiebar.min",
        "nice-select":          "/static/bower_components/jquery-nice-select/js/jquery.nice-select.min",
        "bootstrap-table":      "/static/bower_components/bootstrap-table/dist/bootstrap-table.min",
        "bootstrap-table-pl":   "/static/bower_components/bootstrap-table/dist/locale/bootstrap-table-pl-PL.min",
        "easing":               "/static/bower_components/jquery.easing/js/jquery.easing.min",
        "jquery.datatables":    "/static/bower_components/datatables/media/js/jquery.dataTables.min",
        "datatables":           "/static/bower_components/datatables/media/js/dataTables.bootstrap.min",
        "templates":            "/static/templates",
        "main":                 "/static/js/main",
        "router":               "/static/js/router",
        "lib":                  "/static/js",
        "locales":              "/static/bower_components/bootstrap-table/dist/locale/",
    },
    shim: {
        "bootstrap": ["jquery",],
        "datatables": ["bootstrap", "jquery.datatables"],
        "bootstrap-table": ["bootstrap"],
        "router": ["bootstrap-table",],
        "easing": ["bootstrap-table",],
        "signals": ["bootstrap-table",],
        "text": ["bootstrap-table",],
        "hasher": ["bootstrap-table",],
        "crossroads": ["bootstrap-table",],
        "handlebars": ["bootstrap-table",],
        "fullcalendarpl" : ["fullcalendar"]
  }
};
