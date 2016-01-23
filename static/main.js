function drawElements(jsonData) {

    var html = '<table class="table table-hover">';
        html += '<tr><th></th><th>Course Id</th><th>Term Id</th><th>Course Name</th></tr></tr>'
        html += '<tbody>'
        $.each(jsonData['course_editions'], function(key, value){
            html += '<tr><td>' + key + '</td><td>' + value[0]['course_id'] + '</td><td>' + value[0]['term_id'] + '</td><td>' + value[0]['course_name']['pl']+ '</td></tr>';
        });
    html += '</tbody></table>';
    $('#school-grades-id').html(html);
}

function drawError(data) {
    var html = '<div class="alert alert-danger" role="alert"><strong>' + 'Error while retrieving data' + '</strong>' + data.responseText.toString() + '</div>';

    $('#school-grades-id').html(html);
}

$( document ).ready(function() {

    //userSecureCookie = Cookies.getJSON('USER_SECURE_COOKIE'); //TODO

    args = {
        'access_token_key': Cookies.getJSON('access_token_key')
        , 'access_token_secret': Cookies.getJSON('access_token_secret')
        , 'mobile_id': Cookies.getJSON('mobile_id')
        , 'usos_id': Cookies.getJSON('usos_id')
    }

    $.ajax({
      type: 'GET',
      url: 'http://localhost:8888/api/courses',
      data: $.param(args),
      success:  function (data) {
            drawElements(JSON.parse(data));
      },
      error: function (err) {
        drawError(err);
      }
  });
});
