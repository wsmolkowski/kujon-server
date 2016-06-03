/*globals jQuery, window, document */
(function ($, window, document) {
    "use strict";
    window.PAGE = window.PAGE || {
        init: function () {
            // this.hack();
            this.slide();
        },
        slide: function () {
            var $table = $('.table');

            $table.on('expand-row.bs.table', function (e, index, row, $detail) {
                var res = $("#" + row._data.details).html();
                $detail.html(res);
            });

            $table.on("click-row.bs.table", function(e, row, $tr) {
                // In my real scenarion, trigger expands row with text detailFormatter..
                //$tr.find(">td>.detail-icon").trigger("click");
                $tr.find(">td>.detail-icon").triggerHandler("click");
            });
        },
        hack: function () {
            $('.table').find('thead th:first-child').remove();
            $('.table').find('thead th:last-child').after('<th></th>');
            $('.table').find('tbody tr').each(function () {
                var $thisClone = $(this).find('td:first-child').clone(true);
                $(this).find('td:last-child').after($thisClone);
                $(this).find('td:first-child').remove();
            });
        },

    };
    $(document).on('ready', function () {
        window.PAGE.init();
    });
}(jQuery, window, document));
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




});

 //jQuery to collapse the navbar on scroll
$(window).scroll(function() {
    if ($(".navbar").offset().top > 50) {
        $(".navbar-fixed-top").addClass("top-nav-collapse");
    } else {
        $(".navbar-fixed-top").removeClass("top-nav-collapse");
    }
});

//jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top - 70
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
});


		$(document).ready(function(){
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
		});
	$(document).ready(function() {
    $('#table-wykladowcy').DataTable();
} );
$('#table-oceny').bootstrapTable({
    classes: "table-hover",
	pagination: true,
	sortName: "name"
});
$('#table-oceny').bootstrapTable({
    classes: "table-hover",
	pagination: true,
	sortName: "name"
});