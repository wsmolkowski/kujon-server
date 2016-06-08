define(['jquery', 'scripts', 'bootstrap', 'router', 'datatables'],
function($, scripts, bootstrap, router, datatables) {

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

});
