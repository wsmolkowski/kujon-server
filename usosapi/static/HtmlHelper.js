function HtmlHelper() {
    var self = this;

    function generateHeader(obj) {
        var tableHeader = '<thead><tr>';
        var first = obj[0];
        for (var prop in first) {
            if (first.hasOwnProperty(prop)) {
                tableHeader += '<th>' + prop + '</th>';
            }
        }
        tableHeader += '</tr></thead>';
        return tableHeader;
    }

    function generateRows(obj){
        var rows = '';
        for (var prop in obj) {
            if (obj.hasOwnProperty(prop)) {
                var tableRow = '';
                if (typeof obj[prop] != "function" && typeof obj[prop] != "object") {
                    tableRow = '<td>' + obj[prop] + '</td>';
                } else if (typeof obj[prop] === "object") {
                    rows += '<tr>' + generateRows(obj[prop]) + '</tr>';
                }
                rows += tableRow;
            }
        }
        return rows;
    }

    self.generateTable = function(obj) {
        var table = '<table class="table table-striped table-bordered">';
        table += generateHeader(obj);
        table += '<tbody>';
        table += generateRows(obj);
        table += '</tbody></table>';
        return table;
    }
};