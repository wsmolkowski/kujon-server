function drawElements(jsonData) {

    var html = '<table class="table table-hover">';
        html += '<tr><th>Term</th><th>Course Id</th><th>Course Name</th><th>Action</th></tr></tr>'
        html += '<tbody>'
        $.each(jsonData['course_editions'], function(key, value){
            html += '<tr>'
            html += '<td><a href=term_info?term_id='+encodeURIComponent(value[0]['term_id'])+'>' + value[0]['term_id'] + '</a>  </td>'
            html += '<td>' + value[0]['course_id'] + '</td>'
            html += '<td><a href=course_info?course_id='+ value[0]['course_id']+ '&term_id='+value[0]['term_id']+'>' + value[0]['course_name']['pl']+ '</a></td>'
            html += '<td>'
            html += '<a href=grades?course_id='+ value[0]['course_id']+ '&term_id='+encodeURIComponent(value[0]['term_id'])+'>Show grades >></a>&nbsp;&nbsp;'
            html += '<a href=grades?course_id='+ value[0]['course_id']+ '&term_id='+value[0]['term_id']+'>Show friends >></a>'
            html += '</td>'
            html += '</tr>';
        });
    html += '</tbody></table>';
    $('#school-courses-id').html(html);
}

function drawError(data) {
    var html = '<div class="alert alert-danger" role="alert"><strong>' + 'Error while retrieving data' + '</strong>' + data.responseText.toString() + '</div>';

    $('#school-courses-id').html(html);
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
