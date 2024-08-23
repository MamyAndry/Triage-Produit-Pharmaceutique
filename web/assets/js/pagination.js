$(document).ready(function () {
    const rowsPerPage = 20; // Number of rows per page
    let currentPage = 1; // Current page number
    
    // Function to fetch data from server
    function fetchData(curr_page) {
        curr_page = parseInt(curr_page); // Convert input to an integer
        if (curr_page < 1 || curr_page > totalPages || isNaN(curr_page)) return; // Validate the page number

        // AJAX request to fetch data for the specific page
        $.ajax({
            url: 'http://127.0.0.1:5000/fetch_data',
            type: 'GET',
            data: { page: curr_page, rows_per_page: rowsPerPage },
            success: function (response) {
                updateTable(response.data);
                setupPagination(response.totalPages, curr_page); // Update pagination with new current page
            },
            error: function (xhr, status, error) {
                console.error("Error fetching data:", error);
            }
        });
    }

    // Function to update the table with fetched data
    function updateTable(data) {
        $('#myTable tbody').empty(); // Clear the existing table body

        $.each(data, function (index, row) {
            $('#myTable tbody').append(`
                <tr>
                    <td>${row[0]}</td>
                    <td>${row[1]}</td>
                    <td>${row[2]}</td>
                    <td>${row[3]}</td>
                    <td>${row[4]}</td>
                </tr>
            `);
        });
    }

    // Helper function to create pagination button
    function createButton(page, text, disabled = false) {
        console.log("ito e " + page);
        return `<li class="page-item ${disabled ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="fetchPage(${page})">${text}</a>
                </li>`;
    }

    // Function to setup pagination controls
    function setupPagination(totalPages, currentPage) {
        const paginationContainer = $('#pagination'); // Your pagination container
    
        paginationContainer.empty(); // Clear existing pagination links
    
        // Previous button
        paginationContainer.append(createButton((currentPage - 1), '<', currentPage === 1));
    
        // "Go to page" scrollable input
        paginationContainer.append(`
            <li class="page-item">
                <input type="number" min="1" max="${totalPages}" value="${currentPage}" 
                       onchange="fetchPage(this.value)" class="page-input" style="width: 60px;"/>
            </li>
        `);
    
        // Next button
        paginationContainer.append(createButton((currentPage + 1), '>', currentPage === totalPages));
    }

    
    // Initial data fetch
    fetchData(currentPage);
});
