var params = {};

if (location.search) {
    var parts = location.search.substring(1).split('&');

    for (var i = 0; i < parts.length; i++) {
        var nv = parts[i].split('=');
        if (!nv[0]) continue;
        params[nv[0]] = nv[1] || true;
    }
}

function drawElements(jsonData) {

    var html = '<table class="table table-hover">';
        html += '<tr><th>Course name</th><th>Term Id</th></tr>'
        html += '<tbody>'
        html += '<tr><td>' + jsonData['course_name']['pl'] + '</td><td>' + jsonData['term_id'] +'</td></tr>'
        html += '</tbody></table>';
        html += '<table class="table table-hover">';
        html += '<tr><th>No</th><th>Grade</th><th>Grade name</th></tr>'
        html += '<tbody>'
        $.each(jsonData['grades']['course_grades'], function(key, value){
            html += '<tr>'
            html += '<td>' + key + '</td>'
            html += '<td>' + value['value_symbol'] + '</td>'
            html += '<td>' + value['value_description']['pl'] + '</td>'
            html += '</tr>';
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
        , 'course_id': params.course_id
        , 'term_id': params.term_id
    }

    $.ajax({
      type: 'GET',
      url: 'http://localhost:8888/api/grades',
      data: $.param(args),
      success:  function (data) {
            drawElements(JSON.parse(data));
      },
      error: function (err) {
        drawError(err);
      }
  });
});
