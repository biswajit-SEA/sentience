document.addEventListener("DOMContentLoaded", function () {
  // Toast notification system
  function showToast(message, isError = false) {
    const toastContainer = document.getElementById("toastContainer");

    // Create toast element
    const toast = document.createElement("div");
    toast.className = `toast ${isError ? "error" : ""}`;

    // Add content to toast
    toast.innerHTML = `
                <div class="toast-message">${message}</div>
                <button class="close-toast">&times;</button>
            `;

    // Add toast to container
    toastContainer.appendChild(toast);

    // Set timeout to trigger animation after adding to DOM
    setTimeout(() => {
      toast.querySelector(".close-toast").addEventListener("click", () => {
        removeToast(toast);
      });

      setTimeout(() => {
        removeToast(toast);
      }, 5000);
    }, 10);
  }

  function removeToast(toast) {
    toast.style.animation = "fadeOut 0.3s forwards";

    // Remove from DOM after animation completes
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  }

  // Delete functionality
  const deleteModal = document.getElementById("deleteModal");
  const deleteUserNameElement = document.getElementById("deleteUserName");
  let userIdToDelete = null;

  // Add event listeners to all delete buttons
  document.querySelectorAll(".delete-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const userId = this.getAttribute("data-user-id");
      const userName = this.getAttribute("data-user-name");

      userIdToDelete = userId;
      deleteUserNameElement.textContent = userName;
      deleteModal.style.display = "flex";
    });
  });

  // Cancel delete
  document
    .querySelectorAll("#deleteModal .cancel-btn, #deleteModal .close-button")
    .forEach((button) => {
      button.addEventListener("click", function () {
        deleteModal.style.display = "none";
        userIdToDelete = null;
      });
    });

  // Confirm delete
  document
    .querySelector("#deleteModal .confirm-delete-btn")
    .addEventListener("click", function () {
      // Get the CSRF token from the page (needed for secure POST requests)
      const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

      // Show loading state
      const deleteBtn = this;
      const originalText = deleteBtn.textContent;
      deleteBtn.textContent = "Deleting...";
      deleteBtn.disabled = true;

      // Debug info
      console.log(`Attempting to delete user with ID: ${userIdToDelete}`);
      console.log(`CSRF Token: ${csrfToken ? "Present" : "Missing"}`);

      // Send AJAX request to delete the user
      fetch(`/admin/delete_user/${userIdToDelete}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
          "X-Requested-With": "XMLHttpRequest",
        },
        credentials: "same-origin",
      })
        .then((response) => {
          console.log(`Response status: ${response.status}`);
          if (!response.ok) {
            return response.json().then((data) => {
              throw new Error(data.message || "Server error occurred");
            });
          }
          return response.json();
        })
        .then((data) => {
          console.log("Success response:", data);

          // Hide the modal
          deleteModal.style.display = "none";

          // Remove the user row from the table or refresh the page
          const userRow = document.querySelector(
            `tr[data-user-id="${userIdToDelete}"]`
          );
          if (userRow) {
            console.log("Found user row, removing from DOM");
            userRow.remove();
          } else {
            console.log("User row not found, reloading page");
            // Refresh the page if we can't find the row
            window.location.reload();
          }

          // Show success toast
          showToast(`User has been deleted successfully`);

          // Reset state
          userIdToDelete = null;
        })
        .catch((error) => {
          console.error("Error details:", error);
          showToast(
            `Failed to delete user: ${error.message || "Unknown error"}`,
            true
          );
        })
        .finally(() => {
          // Reset button state
          deleteBtn.textContent = originalText;
          deleteBtn.disabled = false;
        });
    });

  // Edit functionality
  const editModal = document.getElementById("editModal");
  const editUserIdInput = document.getElementById("editUserId");
  const editNameInput = document.getElementById("editName");
  const editEmailInput = document.getElementById("editEmail");
  const editRoleSelect = document.getElementById("editRole");

  // Add event listeners to all edit buttons
  document.querySelectorAll(".edit-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const userId = this.getAttribute("data-user-id");
      const userName = this.getAttribute("data-user-name");
      const userEmail = this.getAttribute("data-user-email");
      const userRole = this.getAttribute("data-user-role");

      editUserIdInput.value = userId;
      editNameInput.value = userName;
      editEmailInput.value = userEmail;
      editRoleSelect.value = userRole.toLowerCase();

      editModal.style.display = "flex";
    });
  });

  // Cancel edit
  document
    .querySelectorAll("#editModal .cancel-btn, #editModal .close-button")
    .forEach((button) => {
      button.addEventListener("click", function () {
        editModal.style.display = "none";
      });
    });

  // Submit edit form
  document
    .getElementById("editUserForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();

      // Get form values
      const userId = editUserIdInput.value;
      const name = editNameInput.value;
      const email = editEmailInput.value;
      const role = editRoleSelect.value;

      // Get the CSRF token from the page
      const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

      // Show loading state on the button
      const saveBtn = document.querySelector("#editModal .save-btn");
      const originalText = saveBtn.textContent;
      saveBtn.textContent = "Saving...";
      saveBtn.disabled = true;

      // For debugging
      console.log("Sending update with role:", role);

      // Send AJAX request to update the user
      fetch("/admin/update_user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify({
          userId: userId,
          name: name,
          email: email,
          role: role,
        }),
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) {
            return response.json().then((data) => {
              throw new Error(data.message || "Network response was not ok");
            });
          }
          return response.json();
        })
        .then((data) => {
          console.log("Success:", data);

          // Updating the row in the table with new values
          const userRow = document.querySelector(
            `tr[data-user-id="${userId}"]`
          );
          if (userRow) {
            userRow.cells[1].textContent = name;
            userRow.cells[2].textContent = email;
            userRow.cells[3].textContent =
              role.charAt(0).toUpperCase() + role.slice(1);

            // Updating data attributes for the edit button
            const editButton = userRow.querySelector(".edit-btn");
            editButton.setAttribute("data-user-name", name);
            editButton.setAttribute("data-user-email", email);
            editButton.setAttribute("data-user-role", role);
          } else {
            window.location.reload();
          }

          // Showing success toast
          showToast(`User data has been updated successfully`);

          // Hiding the modal
          editModal.style.display = "none";
        })
        .catch((error) => {
          console.error("Error:", error);
          showToast("Failed to update user: " + error.message, true);
        })
        .finally(() => {
          // Resetting button state
          saveBtn.textContent = originalText;
          saveBtn.disabled = false;
        });
    });

  // Close modals when clicking outside
  window.addEventListener("click", function (event) {
    if (event.target === deleteModal) {
      deleteModal.style.display = "none";
      userIdToDelete = null;
    }
    if (event.target === editModal) {
      editModal.style.display = "none";
    }
    if (event.target === resetPasswordModal) {
      resetPasswordModal.style.display = "none";
      document.getElementById("tempPasswordContainer").style.display = "none";
    }
  });

  // Password Reset functionality
  const resetPasswordModal = document.getElementById("resetPasswordModal");
  const resetPasswordUserNameElement = document.getElementById(
    "resetPasswordUserName"
  );
  const tempPasswordContainer = document.getElementById(
    "tempPasswordContainer"
  );
  const tempPasswordElement = document.getElementById("tempPassword");
  const copyPasswordBtn = document.getElementById("copyPasswordBtn");
  let userIdToResetPassword = null;

  // Adding event listeners to all reset password buttons
  document.querySelectorAll(".reset-pwd-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const userId = this.getAttribute("data-user-id");
      const userName = this.getAttribute("data-user-name");

      userIdToResetPassword = userId;
      resetPasswordUserNameElement.textContent = userName;
      tempPasswordContainer.style.display = "none";
      resetPasswordModal.style.display = "flex";
    });
  });

  // Cancel password reset
  document
    .querySelectorAll(
      "#resetPasswordModal .cancel-btn, #resetPasswordModal .close-button"
    )
    .forEach((button) => {
      button.addEventListener("click", function () {
        resetPasswordModal.style.display = "none";
        userIdToResetPassword = null;
        tempPasswordContainer.style.display = "none";
      });
    });

  // Copy password to clipboard
  copyPasswordBtn.addEventListener("click", function () {
    const tempPassword = tempPasswordElement.textContent;
    navigator.clipboard
      .writeText(tempPassword)
      .then(() => {
        this.textContent = "Copied!";
        setTimeout(() => {
          this.textContent = "Copy";
        }, 2000);
      })
      .catch((err) => {
        console.error("Could not copy text: ", err);
        showToast(
          "Failed to copy password. Please select and copy manually.",
          true
        );
      });
  });

  // Confirm password reset
  document
    .querySelector("#resetPasswordModal .confirm-reset-pwd-btn")
    .addEventListener("click", function () {
      // Get the CSRF token from the page
      const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

      // Show loading state
      const resetBtn = this;
      const originalText = resetBtn.textContent;
      resetBtn.textContent = "Resetting...";
      resetBtn.disabled = true;

      // Debug info
      console.log(
        `Attempting to reset password for user with ID: ${userIdToResetPassword}`
      );
      console.log(`CSRF Token: ${csrfToken ? "Present" : "Missing"}`);

      // Send AJAX request to reset the password
      fetch("/admin/reset_password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          userId: userIdToResetPassword,
        }),
        credentials: "same-origin",
      })
        .then((response) => {
          console.log(`Response status: ${response.status}`);
          if (!response.ok) {
            return response.json().then((data) => {
              throw new Error(data.message || "Server error occurred");
            });
          }
          return response.json();
        })
        .then((data) => {
          console.log("Success response:", data);

          // Show the temporary password
          if (data.temp_password) {
            tempPasswordElement.textContent = data.temp_password;
            tempPasswordContainer.style.display = "block";
          }

          // Show success toast
          showToast(`Password has been reset successfully`);

          // Update UI and reset button state
          resetBtn.textContent = originalText;
          resetBtn.disabled = false;
        })
        .catch((error) => {
          console.error("Error details:", error);
          resetPasswordModal.style.display = "none";
          showToast(
            `Failed to reset password: ${error.message || "Unknown error"}`,
            true
          );

          // Reset button state
          resetBtn.textContent = originalText;
          resetBtn.disabled = false;
        });
    });
});
