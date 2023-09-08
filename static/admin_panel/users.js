import {getToken} from "./admin_panel.js";

export function initializeUserManagementSection() {

    function populateUserTable() {
        const userTableDiv = document.getElementById("userTable");

        while (userTableDiv.rows.length > 1) {
            userTableDiv.deleteRow(1);
        }

        fetch(`/admin/users/?token=${getToken()}`)
            .then(response => response.json())
            .then(users => {
                users.forEach(user => {
                    const row = userTableDiv.insertRow();
                    row.insertCell().textContent = user.age;
                    row.insertCell().textContent = user.gender;
                    row.insertCell().textContent = user.occupation;
                    row.insertCell().textContent = user.location;
                    row.insertCell().textContent = user.language;
                    row.insertCell().textContent = user.user_id;
                    row.insertCell().textContent = user.api_prompt_tokens;
                    row.insertCell().textContent = user.api_completion_tokens;
                    row.insertCell().textContent = user.api_total_tokens;
                    row.insertCell().textContent = user.last_token_update_time;
                    row.insertCell().textContent = user.available_tokens;
                    row.insertCell().textContent = user.last_request_time;


                    const deleteBtn = document.createElement("button");
                    deleteBtn.textContent = "Delete";
                    deleteBtn.addEventListener("click", () => deleteUser(user.user_id));
                    row.insertCell().appendChild(deleteBtn);
                });
            })
            .catch(error => {
                console.error("Error fetching users:", error);
            });
    }


    function deleteUser(userId) {
        fetch(`/admin/users/delete/${userId}/?token=${getToken()}`, {
            method: "DELETE"
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                populateUserTable(); // Refresh the user list after deletion
            })
            .catch(error => {
                console.error("Error deleting user:", error);
            });
    }

    populateUserTable();
}