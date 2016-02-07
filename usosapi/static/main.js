var baseContainer = '#base-container-id';
var htmlHelper = new HtmlHelper();

function drawErrorMessage(data) {
    $(baseContainer).empty();
    if ((typeof data) == 'string'){
        var html = '<div class="alert alert-warning" role="alert"><strong>' + 'Error while retrieving data: ' + '</strong>' + data + '</div>';
    }
    else {
        var html = '<div class="alert alert-danger" role="alert"><strong>' + 'Exception while retrieving data: ' + '</strong>' + data.responseText.toString() + '</div>';
    }
    $(baseContainer).html(html);
}

function drawCoursesTable(jsonData) {
    $(baseContainer).empty();

    var html = '<table class="table table-hover">';
        html += '<tr><th>Semestr</th><th>Nr kursu</th><th>Nazwa kursu</th><th></th></tr></tr>'
        html += '<tbody>'
        for (var term in jsonData['course_editions']) {
            for (var course in jsonData['course_editions'][term]) {
                html += '<td><a href=/school/terms/'+encodeURIComponent(jsonData['course_editions'][term][course]['term_id'])+'>' + jsonData['course_editions'][term][course]['term_id'] + '</a>  </td>'
                html += '<td>' + jsonData['course_editions'][term][course]['course_id'] + '</td>'
                html += '<td><a href=/school/courses/'+ jsonData['course_editions'][term][course]['course_id']+ '>' + jsonData['course_editions'][term][course]['course_name']['pl']+ '</a></td>'
                html += '<td>'
                html += '<a href=/school/grades/course/'+ jsonData['course_editions'][term][course]['course_id']+ '/'+encodeURIComponent(jsonData['course_editions'][term][course]['term_id'])+'>Oceny</a>'
                html += '</td>'
                html += '</tr>';
            }
        }
    html += '</tbody></table>';
    $(baseContainer).html(html);
}

function fetchCursesAndDraw(){
    $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courseseditions',
      success:  function (data) {
            data = JSON.parse(data);
            if (data.status == 'success'){
                drawCoursesTable(data.data);
            } else {
                drawErrorMessage(data.message);
            }
      },
      error: function (err) {
        drawErrorMessage(err);
      }
    });
}

function drawCourseInfoTable(jsonData){
    $(baseContainer).empty();
     var html = '<table class="table table-hover">';
        html += '<tr><th>Numer przedmiotu</th><th>Nazwa przedmiotu</th><th>Opis</th><th></th></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['course_id'] + '</td>'
        html += '<td>' + jsonData['name']['pl'] + '</td>'
        html += '<td>' + jsonData['description']['pl'] + '</td>'
        html += '</tr>'
        html += '</tbody></table>';
    $(baseContainer).html(html);
}

function drawGradesTable(grades){

    $(baseContainer).empty();

    var html = '<table class="table table-hover">';
    html += '<tr><th>Semestr</th><th>Kurs</th><th>Nazwa kursu</th><th></th></tr>'
    html += '<tbody>'
    for (var key in grades) {
                html += '<tr>'
                html += '<td><a href=/school/terms/' + encodeURIComponent(grades[key]['term_id']) + '>' + grades[key]['term_id'] + '</a></td>'
                html += '<td><a href=/school/courses/' + grades[key]['course_id']+'>' + grades[key]['course_id'] + '</a></td>'
                html += '<td>' + grades[key]['course_name']['pl'] + '</td>'
                html += '<td><table class="table table-hover">'

                var pom = grades[key]['grades']['course_grades']
                if (typeof pom != 'undefined') {
                    html += '<tr><th>Ocena</th><th>Słownie</th><th>Termin</th></tr>'

                    for (var exam in grades[key]['grades']['course_grades']) {
                        html += '<tr>'
                        html += '<td>' + grades[key]['grades']['course_grades'][exam]['value_symbol'] + '</td>'
                        html += '<td>' + grades[key]['grades']['course_grades'][exam]['value_description']['pl'] + '</td>'
                        html += '<td>' + grades[key]['grades']['course_grades'][exam]['exam_session_number'] + '</td>'
                        html += '</tr>'
                    }
                }
                else {
                    html += '<tr><th>zajęcia</th><th>ocena</th><th>słownie</th><th>termin</th></tr>'
                    for (var unit in grades[key]['grades']['course_units_grades']) {
                        for (var pass in grades[key]['grades']['course_units_grades'][unit]) {
                            html += '<tr>'
                            html += '<td>' + grades[key]['grades']['course_units'][unit]['classtype_id'] + '</td>'
                            html += '<td>' + grades[key]['grades']['course_units_grades'][unit][pass]['value_symbol'] + '</td>'
                            html += '<td>' + grades[key]['grades']['course_units_grades'][unit][pass]['value_description']['pl'] + '</td>'
                            html += '<td>' + grades[key]['grades']['course_units_grades'][unit][pass]['exam_session_number'] + '</td>'
                            html += '</tr>'
                        }
                    }
                }

                html += '</td></table>'
                html += '</tr>'
    }
    html += '</tbody></table>';
    $(baseContainer).html(html);
}

function drawGradeTable(jsonData){
    $(baseContainer).empty();
     var html = '<table class="table table-hover">';
        html += '<tr><th>Przedmiot</th><th>Numer przedmiotu</th></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td><a href=/school/courses/' + jsonData['course_id'] + '>' + jsonData['course_name']['pl'] + '</a></td>'
        html += '<td>' + jsonData['course_id'] + '</td>'
        html += '</tr>'
        html += '</tbody></table>';

        html += '<table class="table table-hover">';
        if (typeof jsonData['grades']['course_grades'] != 'undefined') {
            html += '<tr><th>Nr egzaminu</th><th>Termin egzaminu</th><th>Ocena</th><th>Ocena opisowa</th></tr>'
            html += '<tbody>'
            for (exam in jsonData['grades']['course_grades']) {
                html += '<tr>'
                html += '<td>' + jsonData['grades']['course_grades'][exam]['exam_id']+ '</td>'
                html += '<td>' + jsonData['grades']['course_grades'][exam]['exam_session_number']+ '</td>'
                html += '<td>' + jsonData['grades']['course_grades'][exam]['value_symbol']+ '</td>'
                html += '<td>' + jsonData['grades']['course_grades'][exam]['value_description']['pl']+ '</td>'
                html += '</tr>'
            }
        }
        else {
            html += '<tr><th>Zajęcia</th><th>Termin</th><th>Ocena</th><th>Ocena opisowa</th></tr>'
            html += '<tbody>'
            for (exam in jsonData['grades']['course_units_grades']) {
                for (term in jsonData['grades']['course_units_grades'][exam]) {
                    html += '<tr>'
                    html += '<td>' + jsonData['grades']['course_units'][exam]['classtype_id']+ '</td>'
                    html += '<td>' + jsonData['grades']['course_units_grades'][exam][term]['exam_session_number']+ '</td>'
                    html += '<td>' + jsonData['grades']['course_units_grades'][exam][term]['value_symbol']+ '</td>'
                    html += '<td>' + jsonData['grades']['course_units_grades'][exam][term]['value_description']['pl']+ '</td>'
                    html += '</tr>'
                }
            }
        }
        html += '</tbody></table>';
    $(baseContainer).html(html);
}

function fetchCurseInfo(courseId){
     $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courses/' + courseId,
      success:  function (data) {
            data = JSON.parse(data);
            if (data.status == 'success'){
                drawCourseInfoTable(data.data);
            } else {
                drawErrorMessage(data.data);
            }
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
                data = JSON.parse(data);
                if (data.status == 'success'){
                    drawGradeTable(data.data);
                } else {
                    drawErrorMessage(data.message);
                }
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
                data = JSON.parse(data);

                if (data.status == 'success'){
                    drawGradesTable(data.data);
                } else {
                    drawErrorMessage(data.message);
                }
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
        html += '<tr><th>Nazwa Semestru</th><th>Numer</th><th>Początek</th><th>Koniec</th><th>Zakończenie</th></tr></tr>'
        html += '<tbody>'
        $.each(jsonData, function(key, value){
            html += '<tr>'
            for(var i=0; i< 1; i++) {
                html += '<td><a href=/school/terms/' + encodeURIComponent(value['term_id']) + '>' + value['name']['pl'] + '</a></td>'
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
        html += '<tr><th>Nazwa Semestru</th><th>Numer</th><th>Początek</th><th>Koniec</th><th>Zakończenie</th></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['name']['pl'] + '</td>'
        html += '<td>' + jsonData['term_id'] + '</td>'
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
           url: deployUrl + '/api/terms/'+ termId,
           success:  function (data) {
            data = JSON.parse(data);
            if (data.status == 'success'){
                drawTermTable(data.data);
            } else {
                drawErrorMessage(data.message);
            }
           },
           error: function (err) {
            drawErrorMessage(err);
           }
        });
     } else {
        $.ajax({
           type: 'GET',
           url: deployUrl + '/api/terms',
           success:  function (data) {
           data = JSON.parse(data);
            if (data.status == 'success'){
                drawTermsTable(data.data);
            } else {
                drawErrorMessage(data.message);
            }
           },
           error: function (err) {
            drawErrorMessage(err);
           }
        });
     };


}

function drawFriendsSuggestionsTable(jsonData){

    $(baseContainer).empty();
     var html = '<table class="table table-hover">';
        html += '<tr><th>Imię i Nazwisko</th><th>USOS user ID</th><th>Ilość zajęć razem</th><th></th></tr>'
        html += '<tbody>'
        for(var key in jsonData) {
            html += '<tr>'
            html += '<td><a href=/users/'+ jsonData[key]['user_id'] + '>' + jsonData[key]['first_name'] + ' ' + jsonData[key]['last_name'] + '</td>'
            html += '<td>' + jsonData[key]['user_id'] + '</td>'
            html += '<td>' + jsonData[key]['count'] + '</td>'
            html += '<td><a href="/api/friends/add/'+ jsonData[key]['user_id']  + '">Dodaj</a></td>'
            html += '</tr>'
        }
        html += '</tbody></table>';
    $(baseContainer).html(html);
}

function drawFriendsTable(jsonData){

    $(baseContainer).empty();
     var html = '<table class="table table-hover">';
        html += '<tr><th>Imię i Nazwisko</th><th>USOS user ID</th><th></th></tr>'
        html += '<tbody>'
        for(var key in jsonData) {
            html += '<tr>'
            html += '<td><a href=/users/'+ jsonData[key]['user_id'] + '>' + jsonData[key]['first_name'] + ' ' + jsonData[key]['last_name'] + '</td>'
            html += '<td>' + jsonData[key]['user_id'] + '</td>'
            html += '<td><a href="/api/friends/remove/'+ jsonData[key]['friend_id']  + '">Usuń</a></td>'
            html += '</tr>'
        }
        html += '</tbody></table>';
    $(baseContainer).html(html);
}

function drawUserInfo(jsonData){
    $(baseContainer).empty();

    var html = '<table class="table table-hover">';
    html += '<caption>Informacje z Kujona</caption>'
    html += '<tr><th></th><th></th></tr>'
    html += '<tbody>'
    html += '<tr><td>Email</td><td>asdkajd@asdkasd.com</td></tr>'
    html += '<tr><td>Zarejestrowany</td><td>NIE...</td></tr>'

    html += '</tbody>'
    html += '</table>'
    html += '<table class="table table-hover">';

    html += '<caption>Informacje USOS o użytkowniku</caption>'
    html += '<tr><th></th><th></th></tr>'
    html += '<tbody>'

    html += '<tr><td>Imię</td><td>' + jsonData['first_name'] + '</td></tr>'
    html += '<tr><td>Nazwisko</td><td>' + jsonData['last_name'] + '</td></tr>'
    html += '<tr><td>Student number</td><td>' + jsonData['student_number'] + '</td></tr>'
    html += '<tr><td>Email</td><td>' + jsonData['email'] + '</td></tr>'

    $.each(jsonData['student_programmes'], function(key, value){
            for(var i=1; i< 2; i++) {
                html += '<tr><td>Program</td><td>' + value['programme']['id'] + ' (' + value['id'] + ') - ' + value['programme']['description']['pl']+ '</td></tr>'
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
             url: deployUrl + '/api/friends/suggestions',
             success:  function (data) {
             data = JSON.parse(data);
                 if (data.status == 'success'){
                    drawFriendsSuggestionsTable(data.data);
                 }
                 else {
                    drawErrorMessage(data.message);
                 }
            },
                error: function (err) {
                    drawErrorMessage(err, baseContainer);
                }
       });
}

function fetchFriendsAndDraw(){

       $.ajax({
             type: 'GET',
             url: deployUrl + '/api/friends',
             success:  function (data) {
             data = JSON.parse(data);
                 if (data.status == 'success'){
                    drawFriendsTable(data.data);
                 }
                 else {
                    drawErrorMessage(data.message);
                 }
            },
                error: function (err) {
                    drawErrorMessage(err, baseContainer);
                }
       });
}

function fetchUserInfoAndDraw(user_id) {
    if (typeof user_id != 'undefined'){
        $.ajax({
             type: 'GET',
             url: deployUrl + '/api/users/' + user_id,
             success:  function (data) {
                data = JSON.parse(data);
                if (data.status == 'success'){
                    drawUserInfo(data.data);
                } else {
                    drawErrorMessage(data.message);
                }
             },
             error: function (err) {
                drawErrorMessage(err, baseContainer);
            }
        });
    }
    else {
        $.ajax({
             type: 'GET',
             url: deployUrl + '/api/users',
             success:  function (data) {
                data = JSON.parse(data);
                if (data.status == 'success'){
                    drawUserInfo(data.data);
                } else {
                    drawErrorMessage(data.message);
                }
             },
             error: function (err) {
                drawErrorMessage(err, baseContainer);
            }
        });
    }
}

$( document ).ready(function() {

    var pathname = $(location).attr('pathname');
    var pathSplit = pathname.split('/');
    if (pathname.indexOf('/school/courses') === 0){
        if (pathSplit.length == 3){
            fetchCursesAndDraw();
        }
        else if (pathSplit.length == 4) {
            fetchCurseInfo(pathSplit[3]);
        }
    }
    else if (pathname.indexOf('/school/grades/course/') === 0){
        fetchGradesAndDraw(pathSplit[4],pathSplit[5]);
    }
    else if (pathname.indexOf('/school/grades') === 0){
        fetchGradesAndDraw();
    }
    else if (pathname.indexOf('/school/terms') === 0){
        if (pathSplit.length == 3){
            fetchTermsAndDraw();
        }
        else if (pathSplit.length == 4) {
            fetchTermsAndDraw(pathSplit[3]);
        }
    }
    else if (pathname.indexOf('/friends/suggestions') === 0){
        fetchFriendsSuggestionsAndDraw();
    }
    else if (pathname.indexOf('/friends') === 0){
        fetchFriendsAndDraw();
    }
    else if (pathname.indexOf('/users') === 0){
        fetchUserInfoAndDraw(pathSplit[2]);
    }
});
