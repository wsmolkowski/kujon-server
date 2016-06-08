define(['jquery',  'bootstrap', 'bootstrap-table', 'router', 'datatables'],
function($, bootstrap, bootstrapTable, router, datatables) {

    $(document).ready(function () {
        //stick in the fixed 100% height behind the navbar but don't wrap it
        $('#slide-nav.navbar .container-fluid').append($('<div id="navbar-height-col"></div>'));
        $('#slide-nav.navbar .container').append($('<div id="navbar-height-col"></div>'));
        // Enter your ids or classes
        var toggler = '.navbar-toggle';
        var pagewrapper = '#page-content';
        var navigationwrapper = '.navbar-header';
        var menuwidth = '100%'; // the menu inside the slide menu itself
        var slidewidth = '50%';
        var menuneg = '-100%';
        var slideneg = '-50%';


        $("#slide-nav").on("click", toggler, function (e) {

            var selected = $(this).hasClass('slide-active');

            $('#slidemenu').stop().animate({
                right: selected ? menuneg : '0px'
            });

            $('#navbar-height-col').stop().animate({
                right: selected ? slideneg : '0px'
            });

            $(pagewrapper).stop().animate({
                right: selected ? '0px' : slidewidth
            });

            $(navigationwrapper).stop().animate({
                right: selected ? '0px' : slidewidth
            });


            $(this).toggleClass('slide-active', !selected);
            $('#slidemenu').toggleClass('slide-active');


            $('#page-content, .navbar, body, .navbar-header').toggleClass('slide-active');


        });


        var selected = '#slidemenu, #page-content, body, .navbar, .navbar-header';
        $(window).on("resize", function () {
            if ($(window).width() > 929 && $('.navbar-toggle').is(':hidden')) {
                $(selected).removeClass('slide-active');
            }
        });

        var kolumnaPrawa =  $("div.border-logo-cykle").height();
			var kolumnaLewa = $("div.border-logo-cykle").height();

			if (kolumnaLewa > kolumnaPrawa)
			{
				$("div.border-logo-cykle").css({'height' : kolumnaLewa});
			}
			else
			{
				$("div.border-logo-cykle").css({'height' : kolumnaPrawa});
			};

		$('#table-lecturers, #table-grades, #table-terms, #table-programmes, #table-faculties').DataTable({
            "dom": '<f<t>ilp>',
            language: {
            paginate: {
                first:    '«',
                previous: '‹',
                next:     '›',
                last:     '»'
            },
            aria: {
                paginate: {
                    first:    'pierwsza',
                    previous: 'poprzednia',
                    next:     'następna',
                    last:     'ostatnia'
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
        });
        $('#table-lista-studentow').DataTable({
            "dom": '<f<t>ilp>',
            language: {
            paginate: {
                first:    '«',
                previous: '‹',
                next:     '›',
                last:     '»'
            },
            aria: {
                paginate: {
                    first:    'pierwsza',
                    previous: 'poprzednia',
                    next:     'następna',
                    last:     'ostatnia'
                }
            },


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
	});
        function format(value) {
           return '<div class="slider">'+
                    '<table class="col-sm-12"  cellspacing="0" border="0" style="padding-left:50px;">'+
                        '<tr class="row" >'+
                            '<td class="col-sm-5"><p class="title-courses">Jednostka:</p><p class="opis-courses"><span>Wydział “Artes Liberales” Nowy Świat 69, 00-046 Warszawa (Śródmieście) 835757. 10556168</span></p></td>'+
                            '<td class="col-sm-2"><p class="title-courses">Prowadzący</p><p class="opis-courses"><span>Stefan Białas</span></p></td>'+
                            '<td class="col-sm-2"><p class="title-courses">Krytera oceny:</p><p data-toggle="modal" data-target="#kryteria-grades" class="kryteria-grades"><span>Zobacz kryteria</span></p></td>'+
                            '<td class="col-sm-3"><p class="title-courses">Typ zajęć</p><p class="opis-courses"><span>Konserwatorium, numer grupy: 1</span></p></td>'+
                        '</tr>'+
                        '<tr class="row" >'+
                            '<td class="col-sm-5"><div class="row"><div class="col-sm-6"><p class="title-courses">Język prowadzenia:</p><p class="opis-courses"><span>Polski</span></p></div><div class="col-sm-6"><p class="title-courses">Język prowadzenia:</p><p class="opis-courses"><span>Polski</span></p></div></div></td>'+
                            '<td class="col-sm-2"><p class="title-courses">Opis</p><p class="opis-courses opis-courses" data-toggle="modal" data-target="#opis-courses"><span>Zobacz opis</span></p></td>'+
                            '<td class="col-sm-2"><p class="title-courses">Bibliografia:</p><p class="kryteria-grades opis-courses" data-toggle="modal" data-target="#bibliografia"><span>Zobacz bibliografię</span></p></td>'+
                            '<td class="col-sm-3"><p class="title-courses">Studenci</p><p class="lista-studentow opis-courses" data-toggle="modal" data-target="#zobacz-liste-studentow"><span>Zobacz listę studentów </span></p></td>'+
                        '</tr>'+
                    '</table>'+
                '</div>';
           }
    });

    var table = $('#courses-table').DataTable({"dom": '<f<t>ilp>',
		language: {
        paginate: {
            first:    '«',
            previous: '‹',
            next:     '›',
            last:     '»'
        },
        aria: {
            paginate: {
                first:    'pierwsza',
                previous: 'poprzednia',
                next:     'następna',
                last:     'ostatnia'
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
    }});

      // Add event listener for opening and closing details
      $('#courses-table').on('click', 'td.details-control', function () {
          var tr = $(this).closest('tr');
          var row = table.row(tr);

          if (row.child.isShown()) {
              // This row is already open - close it
              row.child.hide();
              tr.removeClass('shown');
          } else {
              // Open this row
              row.child(format(tr.data('child-value'))).show();
              tr.addClass('shown');
          }
     });

     //jQuery to collapse the navbar on scroll
    $(window).scroll(function() {
        if ($(".navbar").offset().top > 50) {
            $(".navbar-fixed-top").addClass("top-nav-collapse");
        } else {
            $(".navbar-fixed-top").removeClass("top-nav-collapse");
        }
    });

});
