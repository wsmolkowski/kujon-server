var baseContainer = '#base-container-id';
var htmlHelper = new HtmlHelper();

function drawErrorMessage(data) {
    $(baseContainer).empty();

    var html = '<div class="alert alert-danger" role="alert"><strong>' + 'Error while retrieving data: ' + '</strong>' + data.responseText.toString() + '</div>';

    $(baseContainer).html(html);
}

function drawCoursesTable(jsonData) {
    $(baseContainer).empty();

    var html = '<table class="table table-hover">';
        html += '<tr><th>Term</th><th>Course Id</th><th>Course Name</th><th></th></tr></tr>'
        html += '<tbody>'
        $.each(jsonData['course_editions'], function(key, value){
            html += '<tr>'
            for(var i=0; i< value.length; i++) {
                html += '<td><a href=/school/terms/'+encodeURIComponent(value[i]['term_id'])+'>' + value[i]['term_id'] + '</a>  </td>'
                html += '<td>' + value[i]['course_id'] + '</td>'
                html += '<td><a href=/school/courses/'+ value[i]['course_id']+ '>' + value[i]['course_name']['pl']+ '</a></td>'
                html += '<td>'
                html += '<a href=/school/grades/course/'+ value[i]['course_id']+ '/'+encodeURIComponent(value[i]['term_id'])+'>Ocena</a>'
                html += '</td>'
                html += '</tr>';
            }
        });
    html += '</tbody></table>';
    $(baseContainer).html(html);
}

function fetchCursesAndDraw(){
    $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courseseditions',
      //data: $.param(args),
      success:  function (data) {
            drawCoursesTable(JSON.parse(data));
      },
      error: function (err) {
        drawErrorMessage(err);
      }
    });
}

function drawCourseInfoTable(jsonData){
    $(baseContainer).empty();
     var html = '<table class="table table-hover">';
        html += '<tr><th>ID</th><th>Name</th><th>Description</th><th></th></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['course_id'] + '</td>'
        html += '<td>' + jsonData['name']['pl'] + '</td>'
        html += '<td>' + jsonData['description']['pl'] + '</td>'
        html += '</tr>'
        html += '</tbody></table>';
    $(baseContainer).html(html);
}

function drawGradesTable(jsonData){

    $(baseContainer).empty();

    var html = '<table class="table table-hover">';

    var grades = JSON.parse(jsonData);

    for (var k in grades) {
    var g = []
    g = grades[k]['grades']['course_grades']
    if ('1' in g) {
        html += '<tr><th>Term</th><th>Course Id</th><th>Course Name</th><th>Grade</th><th>Description</th><th>Session</th><th>Exam id</th></tr></tr>'
        html += '<tbody>'
        $.each(grades[k]['grades']['course_grades'], function(key, value){
                    html += '<tr>'
                    html += '<td><a href=/school/terms/' + encodeURIComponent(grades[k]['term_id']) + '>' + grades[k]['term_id'] + '</a></td>'
                    html += '<td><a href=/school/courses/' + grades[k]['course_id']+'>' + grades[k]['course_id'] + '</a></td>'
                    html += '<td>' + grades[k]['course_name']['pl'] + '</td>'

                    html += '<td>' + value['value_symbol'] + '</td>'
                    html += '<td>' + value['value_description']['pl'] + '</td>'
                    html += '<td>' + value['exam_session_number'] + '</td>'
                    html += '<td>' + value['exam_id'] + '</td>'
                    html += '</tr>'
        });
    }
    else {
        for (var g in grades) {
                    html += '<tr><th>Term</th><th>Course Id</th><th>Course Name</th><th>Grades</th><th></th></tr></tr>'
                    html += '<tbody>'
                    html += '<tr>'
                    html += '<td><a href=/school/terms/' + encodeURIComponent(grades[k]['term_id']) + '>' + grades[k]['term_id'] + '</a></td>'
                    html += '<td><a href=/school/courses/' + grades[k]['course_id']+'>' + grades[k]['course_id'] + '</a></td>'
                    html += '<td>' + grades[g]['course_name']['pl'] + '</td>'

                    for (var cug in grades[g]['grades']['course_units_grades']) {
//                        html+= '<table class="table table-hover">'
                        html+= '<td>'

                        for (var session in grades[g]['grades']['course_units_grades'][cug]) {
                            html+= '<tr>'
                            grade = grades[g]['grades']['course_units_grades'][cug][session]
                            html += '<td>' + grade['value_symbol'] + '</td>'
                            html += '<td>' + grade['value_description']['pl'] + '</td>'
                            html += '<td>' + grade['exam_session_number'] + '</td>'
                            html += '<td>' + grade['exam_id'] + '</td>'
                            html += '</tr>'
                        }
                        html+= '</td>'

//                         html+= '</table>'
                    }
                    html += '</tr>'

        };
    };
    }
    html += '</tbody></table>';

    $(baseContainer).html(html);
}

function drawGradeTable(jsonData){
    $(baseContainer).empty();
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

        /*
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
        */

    $(baseContainer).html(html);
}

function fetchCurseInfo(courseId){

     $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courses/' + courseId,
      success:  function (data) {
            drawCourseInfoTable(JSON.parse(data));
      },
      error: function (err) {
        drawErrorMessage(err);
      }
    });
}

function fetchGradesAndDraw(courseId, termId){
     if (typeof courseId != 'undefined'){
        $.ajax({
        type: 'GET',
        url: deployUrl + '/api/grades/course/' + courseId + '/' + termId,
        success:  function (data) {
             drawGradeTable(JSON.parse(data));
          },
          error: function (err) {
            drawErrorMessage(err);
          }
        });
     } else {
        $.ajax({
        type: 'GET',
        url: deployUrl + '/api/grades',
        success:  function (data) {
           drawGradesTable(data);
          },
          error: function (err) {
            drawErrorMessage(err);
          }
        });
     }

}

function drawTermsTable(jsonData){
    $(baseContainer).empty();
    var html = '<table class="table table-hover">';
        html += '<tr><th>Term name</th><th>Term ID</th><th>Start date</th><th>End date</th><th>Finish date</th></tr></tr>'
        html += '<tbody>'
        $.each(jsonData, function(key, value){
            html += '<tr>'
            for(var i=0; i< 1; i++) {
                html += '<td>' + value['name']['pl'] + '</td>'
                html += '<td>' + value['term_id'] + '</td>'
                html += '<td>' + value['start_date'] + '</td>'
                html += '<td>' + value['end_date'] + '</td>'
                html += '<td>' + value['finish_date'] + '</td>'
                html += '</tr>';
            }
        });
    html += '</tbody></table>';

    $(baseContainer).html(html);
}

function drawTermTable(jsonData){

    $(baseContainer).empty();
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
    $(baseContainer).html(html);
}

function fetchTermsAndDraw(termId){

     if (typeof termId != 'undefined'){

        $.ajax({
           type: 'GET',
           url: url = deployUrl + '/api/terms/'+ termId,
           success:  function (data) {
            drawTermTable(JSON.parse(data));
           },
           error: function (err) {
            drawErrorMessage(err);
           }
        });

     } else {

        $.ajax({
           type: 'GET',
           url: url = url = deployUrl + '/api/terms',
           success:  function (data) {
            drawTermsTable(JSON.parse(data));
           },
           error: function (err) {
            drawErrorMessage(err);
           }
        });

     };


}

function drawFriendsSuggestionsTable(jsonData){
    $(baseContainer).empty();

    //html = htmlHelper.generateTable(JSON.parse(jsonData));

    $(baseContainer).html(jsonData);
}

function drawUserInfo(jsonData){
    $(baseContainer).empty();

    var html = '<table class="table table-hover">';
    html += '<caption>Informacje USOS o użytkowniku</caption>'
    html += '<tr><th></th><th></th></tr>'
    html += '<tbody>'
    html += '<tr><td>Imię</td><td>' + jsonData['first_name'] + '</td></tr>'
    html += '<tr><td>Nazwisko</td><td>' + jsonData['last_name'] + '</td></tr>'
    html += '<tr><td>Student number</td><td>' + jsonData['student_number'] + '</td></tr>'
    html += '<tr><td>Email</td><td>' + jsonData['email'] + '</td></tr>'

    $.each(jsonData['student_programmes'], function(key, value){
            for(var i=1; i< 2; i++) {
                html += '<tr><td>Program id</td><td>' + value['id'] + '</td></tr>'
                html += '<tr><td>Opis</td><td>' + value['programme']['description']['pl'] + '</td></tr>'
                html += '<tr><td></td><td>' + value['programme']['id'] + '</td></tr>'
            }
    });

    html += '<tr><td></td><td></td></tr>'
    html += '<tr><td></td><td><img src="' + jsonData['photo_urls']['50x50'] + '" class="img-responsive" alt="Responsive image"></td></tr>'
    html += '</tbody></table>';

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

function fetchUserInfoAndDraw() {
    $.ajax({
             type: 'GET',
             url: deployUrl + '/api/user',
             success:  function (data) {
                drawUserInfo(JSON.parse(data));
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
    } else if (pathname.indexOf('/school/grades') === 0){
        fetchGradesAndDraw();
    } else if (pathname.indexOf('/school/terms') === 0){
        if (pathSplit.length == 3){
            fetchTermsAndDraw();
        } else if (pathSplit.length == 4) {
            fetchTermsAndDraw(pathSplit[3]);
        }

    } else if (pathname.indexOf('/friends/suggestions') === 0){
        fetchFriendsSuggestionsAndDraw();
    } else if (pathname.indexOf('/user') === 0){
        fetchUserInfoAndDraw();
    }

});
