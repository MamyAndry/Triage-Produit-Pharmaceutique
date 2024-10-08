
    let searchTermSaved  = "";
    const rowsPerPage = 20; // Number of rows per page
    let currentPage = 1; // Current page number    
    let totalPages = 50;

    // Handle Search AJAX
    $('#searchForm').on('submit', function() {
        let searchTerm = $('#searchBar').val();
        searchTermSaved = searchTerm;
        currentPage = 1;    
        console.log(searchTerm);
        fetchDataSearched(currentPage);
    });

    // Handle File Upload AJAX
    $('#uploadBtn').on('click', function() {
        let formData = new FormData();
        let fileInput = $('#fileInput')[0].files[0];
        let uploadSpinner = $('#uploadSpinner');
        let alert = $('#alert')
        if (fileInput) {
            formData.append('file', fileInput);

            uploadSpinner.removeClass('d-none');
            $('#fileModal').modal('hide');
            $.ajax({
                url: `${API_BASE_URL}/upload`, // Replace with your server URL for file upload
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    alert.empty();
                    uploadSpinner.addClass('d-none');
                    alert.append(`<div class="alert alert-success alert-dismissible" role="alert">
                        FICHIER EXCEL IMPORTE AVEC SUCCES
                    </div>`);
                },
                error: function(xhr, status, error) {
                    uploadSpinner.addClass('d-none');
                    console.error('IMPORTATION ECHOUE: ', status, error);
                },
            });
        } else {
            alert.append(`<div class="alert alert-warning alert-dismissible" role="alert">
                VEUILLEZ SELECTIONNER UN FICHIER A IMPORTER
            </div>`);
        }
    });

    // Function to fetch data from server
    function fetchPage(curr_page) {
        curr_page = parseInt(curr_page); // Convert input to an integer
        if (curr_page < 1 || curr_page > totalPages || isNaN(curr_page)) return; // Validate the page number

        // AJAX request to fetch data for the specific page
        $.ajax({
            url: `${API_BASE_URL}/fetch_data`,
            type: 'GET',
            data: { page: curr_page, rows_per_page: rowsPerPage },
            success: function (response) {
                totalPages = response.totalPages;
                updateTable(response.data);
                setupPagination(response.totalPages, curr_page, "fetchPage"); // Update pagination with new current page
            },
            error: function (xhr, status, error) {
                console.error("Error fetching data:", error);
            }
        });
    }


    // Function to fetch data from server
    function fetchDataSearched(curr_page) {
        curr_page = parseInt(curr_page); // Convert input to an integer
        if (curr_page < 1 || curr_page > totalPages || isNaN(curr_page)) return; // Validate the page number

        // AJAX request to fetch data for the specific page
        $.ajax({
            url: `${API_BASE_URL}/search`,
            type: 'GET',
            cache: false,  // Disable caching
            data: { libelle: searchTermSaved, page: curr_page, rows_per_page: rowsPerPage },
            success: function (response) {
                totalPages = response.totalPages;
                updateTable(response.data);
                setupPagination(response.totalPages, curr_page, "fetchDataSearched"); // Update pagination with new current page
            },
            error: function (xhr, status, error) {
                console.error("Error fetching data:", error);
            }
        });
    }

    function formatTVA(value){
        if(value == "1")
            return "TVA";
        return "";
    }

    // Function to update the table with fetched data
    function updateTable(data) {
        $('#myTable tbody').empty(); // Clear the existing table body

        $.each(data, function (index, row) {
            $('#myTable tbody').append(`
                <tr>
                    <td>${row[0]}</td>
                    <td>${row[1]}</td>
                    <td>${currencyFormatter('fr-FR', 'MGA', row[2])}</td>
                    <td>${formatTVA(row[3])}</td>
                    <td>${dateFormatter(row[4])}</td>
                </tr>
            `);
        });
    }

    // Helper function to create pagination button
    function createButton(page, text, function_called, disabled = false) {
        return `<li class="page-item ${disabled ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="` + function_called + `(${page})">${text}</a>
                </li>`;
    }

    function createLabelMaxPages(){
        const totalPagesLabel = $('#totalPages');
        totalPagesLabel.empty();
        totalPagesLabel.append(`
            <h4>
                Total Pages : <b>${totalPages}</b>
            </h4>`);
    }

    // Function to setup pagination controls
    function setupPagination(totalPages, currentPage, function_called) {
        const paginationContainer = $('#pagination'); // Your pagination container

        paginationContainer.empty(); // Clear existing pagination links
        createLabelMaxPages();
        // Previous button
        paginationContainer.append(createButton((currentPage - 1), '<', function_called, currentPage === 1));

        // "Go to page" scrollable input
        paginationContainer.append(`
            <li class="page-item">
                <input type="number" min="1" max="${totalPages}" value="${currentPage}" 
                        onchange="` + function_called + `(this.value)" class="form-check-input page-input" />
            </li>
        `);

        // Next button
        paginationContainer.append(createButton((currentPage + 1), '>', function_called, currentPage === totalPages));
    }

        