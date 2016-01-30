var cursesElement = '#school-courses-id';
var courseInfoElement = '#course-info-id';
var gradesElement = '#school-grades-id';
var termsElement = '#school-terms-id';
var baseContainer = '#base-container-id';

var htmlHelper = new HtmlHelper();

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
                html += '<td><a href=/school/courses/'+ value[i]['course_id']+ '>' + value[i]['course_name']['pl']+ '</a></td>'
                html += '<td>'
                html += '<a href=/school/grades/course/'+ value[i]['course_id']+ '/'+encodeURIComponent(value[i]['term_id'])+'>Grades</a>'
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
        html += '<tr><th>ID</th><th>Description</th><th>Name</th><th></th></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['course_id'] + '</td>'
        html += '<td>' + jsonData['name']['pl'] + '</td>'
        html += '<td>' + jsonData['description']['pl'] + '</td>'
        html += '</tr>'
        html += '</tbody></table>';
    $(courseInfoElement).html(html);
}

function drawGradesTable(jsonData){
    $(gradesElement).empty();
     var html = '<table class="table table-hover">';
        html += '<tr><th>Course name</th><th>Course id</th></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['course_name']['pl'] + '</td>'
        html += '<td>' + jsonData['course_id'] + '</td>'
        html += '</tr>'
        html += '</tbody></table>';

        html += '<table class="table table-hover">';
        html += '<tr><th>Exam ID</th><th>Exam session</th><th>Grade</th><th>Grade description</th></tr>'
        html += '<tbody>'
        $.each(jsonData['grades']['course_grades'], function(key, value){
            for(var i=1; i< 2; i++) {
                html += '<tr>'
                html += '<td>' + value['exam_id']+ '</td>'
                html += '<td>' + value['exam_session_number']+ '</td>'
                html += '<td>' + value['value_symbol']+ '</td>'
                html += '<td>' + value['value_description']['pl']+ '</td>'
                html += '</tr>'
            }
        });
        html += '</tbody></table>';

        html += '<table class="table table-hover">';
        html += '<tr><th>First name</th><th>Last name</th><th></th></tr>'
        html += '<tbody>'
        count = jsonData['participants'].length
        $.each(jsonData['participants'], function(key, value){
                html += '<tr>'
                html += '<td>' + value['first_name']+ '</td>'
                html += '<td>' + value['last_name']+ '</td>'
                html += '<td><a href=/friends/invite/' + value['user_id']+ '>Zaproś</a></td>'
                html += '</tr>'
        });
        html += '</tbody></table>';

    $(gradesElement).html(html);
}

function fetchCurseInfo(courseId){

     $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courses/' + courseId,
      success:  function (data) {
            drawCourseInfoTable(JSON.parse(data));
      },
      error: function (err) {
        drawErrorMessage(err, courseInfoElement);
      }
    });
}

function fetchGradesAndDraw(courseId,termId){

     $.ajax({
      type: 'GET',
      url: deployUrl + '/api/grades?course_id=' + courseId + '&term_id=' + termId,
      success:  function (data) {
            drawGradesTable(JSON.parse(data));
      },
      error: function (err) {
        drawErrorMessage(err, courseInfoElement);
      }
    });
}

function drawTermsTable(jsonData){
    $(termsElement).empty();
     var html = '<table class="table table-hover">';
        html += '<tr><th>Term ID</th><th>Name</th><th>Start date</th><th>End date</th><th>Finish date</th></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['term_id'] + '</td>'
        html += '<td>' + jsonData['name']['pl'] + '</td>'
        html += '<td>' + jsonData['start_date'] + '</td>'
        html += '<td>' + jsonData['end_date'] + '</td>'
        html += '<td>' + jsonData['finish_date'] + '</td>'
        html += '</tr>'
        html += '</tbody></table>';
    $(termsElement).html(html);
}

function fetchTermsAndDraw(termId){

     $.ajax({
           type: 'GET',
           url: deployUrl + '/api/terms/'+ termId,
           success:  function (data) {
            drawTermsTable(JSON.parse(data));
           },
           error: function (err) {
            drawErrorMessage(err, termsElement);
           }
    });
}

function drawFriendsSuggestionsTable(jsonData){
    $(baseContainer).empty();

    html = htmlHelper.generateTable(JSON.parse(jsonData));

    $(baseContainer).html(html);
}

function fetchFriendsSuggestionsAndDraw(){

       $.ajax({
             type: 'GET',
             url: deployUrl + '/api/fiends/suggestions',
             success:  function (data) {
                drawFriendsSuggestionsTable(JSON.parse(data));
             },
             error: function (err) {
                drawErrorMessage(err, cursesElement);
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
    } else if (pathname.indexOf('/school/grades/course/') === 0){
        fetchGradesAndDraw(pathSplit[4],pathSplit[5]);
    } else if (pathname.indexOf('/school/terms/') === 0){
        fetchTermsAndDraw(pathSplit[3]);
    } else if (pathname.indexOf('/friends/suggestions') === 0){
        fetchFriendsSuggestionsAndDraw();
    }

});
