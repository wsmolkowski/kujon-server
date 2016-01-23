function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
        callback(eval("(" + response + ")"));
    }});
};

$( document ).ready(function() {

    userSecureCookie = Cookies.getJSON('USER_SECURE_COOKIE');
    console.log(userSecureCookie);


    args = {
        'access_token_key': Cookies.getJSON('access_token_key')
        , 'access_token_secret': Cookies.getJSON('access_token_secret')
        , 'mobile_id': Cookies.getJSON('mobile_id')
        , 'usos_id': Cookies.getJSON('usos_id')
    }

    console.log(args);

    $.ajax({
      type: 'GET',
      url: 'http://localhost:8888/api/courses',
      //data: JSON.stringify(args),
      data: $.param(args),
      //dataType: 'json',
      //contentType: 'application/json',
      success:  function (data) {
            alert(JSON.parse(data));
      },
      error: function (err) {
        alert("Error while calling Ajax: " + err.responseText.toString());
      }
  });
});
