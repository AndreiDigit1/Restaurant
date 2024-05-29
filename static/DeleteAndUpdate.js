$(document).ready(function() {
    // Delete client
    $('.delete-btn').click(function() {
        const clientId = $(this).data('id');
        $.ajax({
            url: `/api/delete_client/${clientId}`,
            type: 'DELETE',
            success: function(result) {
                alert(result.message);
                location.reload();
            },
            error: function(xhr) {
                alert(xhr.responseJSON.error);
            }
        });
    });

    // Update client
    $('.update-btn').click(function() {
        var client_id = $(this).data("id");

        // Ask the user which attribute they want to change
        var attributeToChange = prompt("Which attribute would you like to change? (name, surname, age, email, phone)");

        // If the user cancels or provides an invalid attribute, do nothing
        if (!attributeToChange || !["name", "surname", "age", "email", "phone"].includes(attributeToChange.toLowerCase())) {
            return;
        }

        // Prompt for the new value of the selected attribute
        var newValue = prompt("Enter new value for " + attributeToChange + ":");

        // Prepare the data to be sent in the PUT request
        var updateData = {};
        updateData[attributeToChange] = newValue;

        // Send PUT request to update client
        $.ajax({
            type: "PUT",
            url: "/api/update_client/" + client_id,
            contentType: "application/json",
            data: JSON.stringify(updateData),
            success: function(response) {
                alert(response.message);
                // Refresh the page after successful update
                window.location.reload();
            },
            error: function(xhr, status, error) {
                alert("Error updating client: " + error);
            }
        });
    });
});
