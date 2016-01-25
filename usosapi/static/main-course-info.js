function drawElements(jsonData) {

    console.log(jsonData);

    var html = '<table class="table table-hover">';
        html += '<tr><th>ID</th><th>Description</th><th>Name</th><th></th></tr></tr>'
        html += '<tbody>'
        html += '<tr>'
        html += '<td>' + jsonData['id'] + '</td>'
        html += '<td>' + jsonData['description']['pl'] + '</td>'
        html += '<td>' + jsonData['name']['pl'] + '</td>'
        html += '</tr>'

    html += '</tbody></table>';
    $('#course-info-id').html(html);
}

function drawError(data) {
    var html = '<div class="alert alert-danger" role="alert"><strong>' + 'Error while retrieving data' + '</strong>' + data.responseText.toString() + '</div>';

    $('#course-info-id').html(html);
}

$( document ).ready(function() {

    $.ajax({
      type: 'GET',
      url: deployUrl + '/api/courses/' + courseId,
      //data: $.param(args),
      success:  function (data) {
            drawElements(JSON.parse(data));
      },
      error: function (err) {
        drawError(err);
      }
  });
});
