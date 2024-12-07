// Function to fetch data from server
function fetchPage() {
  // AJAX request to fetch data for the specific page
  $.ajax({
    url: `${API_BASE_URL}/classement-furbisher`,
    type: "GET",
    success: function (response) {
      updateTableClassement(response.data);
    },
    error: function (xhr, status, error) {
      console.error("Error fetching data:", error);
    },
  });
}

// Function to update the table with fetched data
function updateTableClassement(data) {
  $("#table-classement tbody").empty(); // Clear the existing table body

  $.each(data, function (index, row) {
    $("#table-classement tbody").append(`
                <tr>
                    <td>${row[1]}</td>
                    <td class="left-item">
                        <form method='get' action="update-classement" class="row g-3">   
                            <div class="col-auto">
                                <input class="form-control" type=number name='classement' value='${row[2]}'>
                            </div>
                            <div class="col-auto">
                                <input type=hidden name='id' value='${row[0]}'>
                            </div>
                            <div class="col-auto">
                                <button type="submit" class="btn btn-primary">Enregitrer</button>
                            </div>
                        </form>
                    </td>
                </tr>
            `);
  });
}

function updateClassementButton(){

}
