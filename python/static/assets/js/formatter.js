
function currencyFormatter(format, devise, valueToFormat){
    // Format as currency
    let formatter = new Intl.NumberFormat(format, {
        style: 'currency',
        currency: devise,
    });
    return formatter.format(parseFloat(valueToFormat));
}

function dateFormatter(dateString){
    // Create a Date object from the string
    let dateObject = new Date(dateString);

    // Format the date to 'DD-MM-YYYY' without time
    let day = dateObject.getUTCDate().toString().padStart(2, '0'); // Get day with leading zero
    let month = (dateObject.getUTCMonth() + 1).toString().padStart(2, '0'); // Months are zero-based, add 1 and pad
    let year = dateObject.getUTCFullYear(); // Get full year

    let formattedDate = `${day}-${month}-${year}`; // Combine in 'DD-MM-YYYY' format

    return formattedDate;
}
