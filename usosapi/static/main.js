var cursesElement = '#school-courses-id';
var courseInfoElement = '#course-info-id';

function drawErrorMessage(data, elementId) {
    $(elementId).empty();

    var html = '<div class="alert alert-danger" role="alert"><strong>' + 'Error while retrieving data' + '</strong>' + data.responseText.toString() + '</div>';

    $(elementId).html(html);
}

function drawCoursesTable(jsonData) {
    $(cursesElement).empty();

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
    $(cursesElement).html(html);
}

function fetchCursesAndDraw(){
    $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courseseditions',
      //data: $.param(args),
      success:  function (data) {
            drawCoursesTable(JSON.parse(data), cursesElement);
      },
      error: function (err) {
        drawErrorMessage(err, cursesElement);
      }
    });
}

function drawCourseInfoTable(jsonData){
    $(courseInfoElement).empty();

     var html = '<table class="table table-hover">';
        html += '<tr><th>ID</th><th>Description</th><th>Name</th><th></th></tr></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['id'] + '</td>'
        html += '<td>' + jsonData['description']['pl'] + '</td>'
        html += '<td>' + jsonData['name']['pl'] + '</td>'
        html += '</tr>'

    html += '</tbody></table>';
    $(courseInfoElement).html(html);
}

function fetchCurseInfo(course){

     $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courses/' + course,
      //data: $.param(args),
      success:  function (data) {
            drawCourseInfoTable(JSON.parse(data));
      },
      error: function (err) {
        drawErrorMessage(err, courseInfoElement);
      }
    });
}

$( document ).ready(function() {

    var pathname = $(location).attr('pathname');
    var pathSplit = pathname.split('/');

    if (pathname.indexOf('/school/courses') === 0){
        if (pathSplit.length == 3){
            fetchCursesAndDraw();
        } else if (pathSplit.length == 4) {
            fetchCurseInfo(pathSplit[3]);
        }
    }

});
