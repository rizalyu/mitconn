document.getElementById('search').addEventListener('keyup', function searchFunction() {
    let input, filter, table, tr, td;
    input = document.getElementById("search");
    filter = input.value.toUpperCase();
    table = document.getElementById("myTable");
    tr = table.getElementsByTagName("tr");

    for (let j = 0; j < tr.length; j++) {
        td = tr[j].getElementsByTagName("td");

        if (td.length > 0) {
            if (td[0].innerHTML.toUpperCase().indexOf(filter) > -1 ||
                td[1].innerHTML.toUpperCase().indexOf(filter) > -1 ||
                td[2].innerHTML.toUpperCase().indexOf(filter) > -1 ||
                td[3].innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[j].style.display = "";
            } else {
                tr[j].style.display = "none";
            }
        }

    }
});