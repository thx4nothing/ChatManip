document.getElementById("userForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form submission

    // Get form values
    var first_name = document.getElementById("firstName").value;
    var last_name = document.getElementById("lastName").value;
    var age = document.getElementById("age").value;
    var invite_code = document.getElementById("invite_code").value;

    // Create JSON object with user information
    var userInfo = {
        first_name: first_name,
        last_name: last_name,
        age: age,
        invite_code: invite_code
    };

    fetch("/create_user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(userInfo)
    })
    .then(response => {
        if (response.redirected) {
            // Get the redirect URL from the response headers
            const redirectUrl = response.url;

            // Manually redirect the user to the new URL
            window.location.href = redirectUrl;
        }
    })
    .catch(error => {
        console.error("Error creating user:", error);
    });

    // Reset the form
    document.getElementById("userForm").reset();
});
