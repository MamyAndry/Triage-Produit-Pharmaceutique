    function addOption(listOfTables) {
        let select = $('#fournisseur');  // Select the <select> element by its ID

        select.empty();

        // Map over the list of tables and append each as an option
        listOfTables.map(function(table) {
            // Create a new option element and append it to the select
            select.append($('<option>', {
                value: table,          // Set the value attribute to the table name
                text: table            // Set the visible text to the table name
            }));
        });
        // Initialize the editableSelect plugin after adding options
        select.editableSelect();
    }

    async function initFurbisherName(){
        try {
            let listOfNames = await fetchFurbisher();
            addOption(listOfNames);
        } catch (error) {
            console.error(error);
        }
    }


    async function fetchFurbisher(){
        return new Promise((resolve, reject) => {
            $.ajax({
                url: `${API_BASE_URL}/furbisher`,
                type: 'GET',
                processData: false,
                contentType: false,
                success: function(response) {
                    resolve(response.data);
                },
                error: function(xhr, status, error) {
                    reject('Erreur lors de la collecte des fournisseurs: ' + error);
                }
            });
        });
    }
    // Clone catalogue div when "Ajouter Catalogue" is clicked
    $("#ajout_cat").on("click", function() {
        // Add a remove button to the cloned div
        let newCatalogue = $(`
        <div class="catalogue">
            <div class="excel_form_inputs">  
                <select type="text" class="form-control" id="fournisseur" name="fournisseur">
                </select>
                <input type="file" class="form-control" id="file_select" name="file">
                <div></div>
                <div class="col-auto">
                    <button type="button" class="btn btn-outline-danger remove-catalogue">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                            <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        `); 
        
        newCatalogue.insertAfter($(this));
        initFurbisherName();
    });

    // Handle removal of cloned catalogue div
    $(document).on("click", ".remove-catalogue", function() {
        $(this).closest(".catalogue").remove();
    });

    // Handle form submission
    $("#excel_form").on("submit", function(e) {
        e.preventDefault();
        
        let formData = new FormData();
        let uploadSpinner = $('#uploadSpinner');
        // Collect all fournisseur inputs and files
        $(".catalogue").each(function(index) {
            let fournisseur = $(this).find("input[name='fournisseur']").val();
            let file = $(this).find("input[type='file']")[0].files[0];
            
            if (fournisseur && file) {
                formData.append('files', file);
                formData.append('fournisseurs', fournisseur);
            }
        });

        // console.log(formData);
        uploadSpinner.removeClass('d-none');
        $.ajax({
            url: `${API_BASE_URL}/upload-catalogue`,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            xhrFields: {
                responseType: 'blob' // to handle file download
            },
            success: function(blob, xhr) {
                let filename = "";
                // If filename is not found in Content-Disposition, use X-Filename
                uploadSpinner.addClass('d-none');
                if (!filename) {
                    const currentDate = new Date();
                    filename = "CATALOGUE_" + dateFormatter(currentDate) + ".xlsx";
                }
                let link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                $("#alert").html('<div class="alert alert-success">Fichier assemblé avec succès. Téléchargement en cours!</div>');
                
            },
            error: function(xhr) {
                uploadSpinner.addClass('d-none');
                console.log(xhr);
                console.log(xhr.getAllResponseHeaders());
                handleErrorResponse(xhr.getResponseHeader("X-Error"));
            }
            
        });
    });
    function handleErrorResponse(response) {
            $("#alert").html('<div class="alert alert-danger">Erreur: ' + response + '</div>');
    }   