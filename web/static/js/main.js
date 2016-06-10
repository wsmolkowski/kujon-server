define("main", ["jquery", "handlebars", "text!templates/error.html"], function($, Handlebars, tplError) {
    /* variables */
    var templateError = Handlebars.compile(tplError);
    var apiUrl = $('#api_url').val();

    var spinner = 0;

    /* private methods */
    function showSpinner() {
        if (spinner < 1) {
            $('#spinner').show();
            spinner++;
        }
    }

    function hideSpinner() {
        if (spinner > 0) {
            $('#spinner').hide();
            spinner = spinner - 1;
        }
    }

    var ajaxGet = function(request_url) {

        return $.ajax({
            type: 'GET',
            url: apiUrl + request_url,
            xhrFields: {
                withCredentials: true
            },
            beforeSend: function() {
                // showSpinner();
            },
            complete: function() {
                // hideSpinner();
            },
            crossDomain: true,
            error: function(jqXHR, exception) {
                var msg = {
                    'message': 'Technical Exception: Response status: ' + jqXHR.status + ' responseText: ' + jqXHR.statusText + ' exception: ' + exception
                };
                $('#section-content').html(templateError(msg));
            }
        });
    };

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
            Handlebars.registerHelper('replspechars', function(string) {
                var pom = (string || '').replace("(", "\\(");
                pom = (pom || '').replace(")", "\\)");
                pom = (pom || '').replace("`", "\\`");
                return pom;
            });
        },
        ajaxGet: ajaxGet,
        getApiUrl: function() {
            return apiUrl;
        },
        getDataTableConfig: function() {
            return {
                "dom": '<f<t>ilp>',
                language: {
                    paginate: {
                        first: '«',
                        previous: '‹',
                        next: '›',
                        last: '»'
                    },
                    aria: {
                        paginate: {
                            first: 'pierwsza',
                            previous: 'poprzednia',
                            next: 'następna',
                            last: 'ostatnia'
                        }
                    },

                    "searchPlaceholder": "Szukaj według nazwy",
                    "info": "Wyświetlanie stron od _PAGE_ z _PAGES_",
                    "lengthMenu": "_MENU_ pozycji na stronę",
                    "sSearch": " ",
                    "sSortAscending": " - kliknij/powrót do sortowania  click/return to sort ascending",
                    "sSortDescending": " - kliknij/powrót do sortowania click/return to sort descending",
                    "sFirst": "Pierwsza strona",
                    "sLast": "Ostatnia strona",
                    "sNext": "Następna strona",
                    "sPrevious": "Poprzednia strona",
                    "sInfoEmpty": "Brak pozycji do pokazania ",
                    "sInfoFiltered": " - filtrowanie z _MAX_ pozycji. ",
                    "sInfoPostFix": " ",
                    "sLengthMenu": "Wyświetla _MENU_ pozycji",
                    "sProcessing": "Tabela jest zajęta",
                    "sZeroRecords": "Brak pozycji do wyświetlenia"
                }
            };
        },
    };

});
