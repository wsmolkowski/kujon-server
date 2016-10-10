define(['jquery', 'handlebars', 'crossroads', 'hasher', 'text!templates/spinner.html'],
    function($, Handlebars, crossroads, hasher, spinnerTpl) {
        'use strict';

        var template = Handlebars.compile(spinnerTpl);

        function setActiveLink(hash) {

            $('#section-content').html(template());

            require(['lib/pages/' + hash], function(page) {
                page.render();

                $('.navbar li.active').removeClass('active'); //trochę gupio ale na szybko
                $('.navbar a[href="#' + hash + '"]').parent().addClass('active');

                //schowaj kręcacz (?)
            });
        }

        crossroads.addRoute('', function() {
            setActiveLink('index');
        });

        // "_=_" is added on callback from facebook - should be removed
        crossroads.addRoute('_=_', function() {
            setActiveLink('index');
        });

        crossroads.addRoute('user/{id}', function(id) {
            setActiveLink('user', id.id);
        });

        crossroads.addRoute('courses/{id}', function(id) {
            setActiveLink('courses', id.id);
        });

        crossroads.addRoute('lecturers/{id}', function(id) {
            setActiveLink('lecturers', id.id);
        });

        var routes = ['index', 'user', 'grades', 'crstests', 'courses', 'terms', 'faculties',
            'programmes', 'lecturers', 'friends', 'friendssuggestions', 'tt', 'contact',
            'search', '404', 'messages'
        ];

        $.each(routes, function(index, value) {
            // console.log(index + ": " + value);
            crossroads.addRoute(value, function() {
                setActiveLink(value);
            });
        });

        function parseHash(newHash, oldHash) {
            crossroads.parse(newHash);
        }

        crossroads.normalizeFn = crossroads.NORM_AS_OBJECT;
        hasher.initialized.add(parseHash);
        hasher.changed.add(parseHash);
        hasher.init();
    });
