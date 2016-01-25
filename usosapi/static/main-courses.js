function drawElements(jsonData) {

    var html = '<table class="table table-hover">';
        html += '<tr><th>Term</th><th>Course Id</th><th>Course Name</th><th></th></tr></tr>'
        html += '<tbody>'
        $.each(jsonData['course_editions'], function(key, value){
            html += '<tr>'
            for(var i=0; i< value.length; i++) {
                html += '<td><a href=terms/'+encodeURIComponent(value[i]['term_id'])+'>' + value[i]['term_id'] + '</a>  </td>'
                html += '<td>' + value[i]['course_id'] + '</td>'
                html += '<td><a href=courses/'+ value[i]['course_id']+ '>' + value[i]['course_name']['pl']+ '</a></td>'
                html += '<td>'
                html += '<a href=grades/courses/'+ value[i]['course_id']+ '/'+encodeURIComponent(value[i]['term_id'])+'>Grades</a>'
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
