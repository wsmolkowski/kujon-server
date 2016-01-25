function drawElements(jsonData) {

    var html = '<table class="table table-hover">';
        html += '<tr><th>Term</th><th>Course Id</th><th>Course Name</th><th>Action</th></tr></tr>'
        html += '<tbody>'
        $.each(jsonData['course_editions'], function(key, value){
            html += '<tr>'
            for(var i=0; i< value.length; i++) {
                html += '<td><a href=term_info?term_id='+encodeURIComponent(value[i]['term_id'])+'>' + value[i]['term_id'] + '</a>  </td>'
                html += '<td>' + value[i]['course_id'] + '</td>'
                html += '<td><a href=course_info?course_id='+ value[i]['course_id']+ '&term_id='+value[i]['term_id']+'>' + value[i]['course_name']['pl']+ '</a></td>'
                html += '<td>'
                html += '<a href=grades?course_id='+ value[i]['course_id']+ '&term_id='+encodeURIComponent(value[i]['term_id'])+'>Show grades >></a>&nbsp;&nbsp;'
                html += '<a href=grades?course_id='+ value[0]['course_id']+ '&term_id='+value[0]['term_id']+'>Show friends >></a>'
                html += '</td>'
                html += '</tr>';
            }
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

    /*
    args = {
        'access_token_key': Cookies.getJSON('access_token_key')
        , 'access_token_secret': Cookies.getJSON('access_token_secret')
        , 'mobile_id': Cookies.getJSON('mobile_id')
        , 'usos_id': Cookies.getJSON('usos_id')
    }
    */

    $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courseseditions',
      //data: $.param(args),
      success:  function (data) {
            drawElements(JSON.parse(data));
      },
      error: function (err) {
        drawError(err);
      }
  });
});
