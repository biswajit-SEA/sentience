# `admin.js` Documentation

## Overview
This JavaScript file implements the functionality for the administrator dashboard of the Customer Churn Prediction System. It provides a dynamic interface for managing user accounts, including user deletion, information editing, and password reset operations.

## Key Features
- Toast notification system for user feedback
- Modal dialogs for confirming critical actions
- AJAX-based user management operations
- Real-time DOM updates without page reloads
- Clipboard integration for temporary passwords
- Error handling with user-friendly messages

## Notification System

### Toast Notifications
A non-intrusive notification system that displays messages at the top of the screen and automatically dismisses after a timeout.

```javascript
function showToast(message, isError = false) {
  const toastContainer = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast ${isError ? "error" : ""}`;
  
  toast.innerHTML = `
    <div class="toast-message">${message}</div>
    <button class="close-toast">&times;</button>
  `;
  
  toastContainer.appendChild(toast);
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    removeToast(toast);
  }, 5000);
}
```

### Toast Animation
Smooth fade-in and fade-out animations for visual polish:

```javascript
function removeToast(toast) {
  toast.style.animation = "fadeOut 0.3s forwards";
  
  // Remove from DOM after animation completes
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  }, 300);
}
```

## User Management Operations

### Delete User Functionality
Allows administrators to safely delete user accounts with confirmation:

1. Displays a confirmation modal with the user's name
2. Sends an AJAX request to the server when confirmed
3. Updates the DOM to remove the user's row from the table
4. Shows a success or error notification

```javascript
document.querySelector("#deleteModal .confirm-delete-btn")
  .addEventListener("click", function() {
    // Send AJAX request to delete the user
    fetch(`/admin/delete_user/${userIdToDelete}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      credentials: "same-origin",
    })
    .then(response => response.json())
    .then(data => {
      // Remove the user row from the table
      const userRow = document.querySelector(`tr[data-user-id="${userIdToDelete}"]`);
      if (userRow) {
        userRow.remove();
      }
      
      // Show success toast
      showToast(`User has been deleted successfully`);
    })
    .catch(error => {
      showToast(`Failed to delete user: ${error.message}`, true);
    });
  });
```

### Edit User Functionality
Allows updating user information including name, email, and role:

1. Populates a modal with the user's current information
2. Validates and submits the form via AJAX
3. Updates the table row with new information
4. Shows success or error notification

```javascript
document.getElementById("editUserForm").addEventListener("submit", function(e) {
  e.preventDefault();
  
  // Get form values
  const userId = editUserIdInput.value;
  const name = editNameInput.value;
  const email = editEmailInput.value;
  const role = editRoleSelect.value;
  
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
  .then(data => {
    // Update the row in the table with new values
    const userRow = document.querySelector(`tr[data-user-id="${userId}"]`);
    if (userRow) {
      userRow.cells[1].textContent = name;
      userRow.cells[2].textContent = email;
      userRow.cells[3].textContent = role.charAt(0).toUpperCase() + role.slice(1);
    }
    
    // Show success toast
    showToast(`User data has been updated successfully`);
  });
});
```

### Password Reset Functionality
Allows administrators to reset a user's password:

1. Displays a confirmation modal
2. Sends an AJAX request to generate a temporary password
3. Displays the temporary password with a copy-to-clipboard button
4. Shows success or error notification

```javascript
document.querySelector("#resetPasswordModal .confirm-reset-pwd-btn")
  .addEventListener("click", function() {
    // Send AJAX request to reset the password
    fetch("/admin/reset_password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      body: JSON.stringify({
        userId: userIdToResetPassword,
      }),
      credentials: "same-origin",
    })
    .then(data => {
      // Show the temporary password
      if (data.temp_password) {
        tempPasswordElement.textContent = data.temp_password;
        tempPasswordContainer.style.display = "block";
      }
      
      // Show success toast
      showToast(`Password has been reset successfully`);
    });
  });
```

## Clipboard Integration

### Copy to Clipboard
Implements a one-click copy function for temporary passwords:

```javascript
copyPasswordBtn.addEventListener("click", function() {
  const tempPassword = tempPasswordElement.textContent;
  navigator.clipboard.writeText(tempPassword)
    .then(() => {
      this.textContent = "Copied!";
      setTimeout(() => {
        this.textContent = "Copy";
      }, 2000);
    })
    .catch(err => {
      showToast("Failed to copy password. Please select and copy manually.", true);
    });
});
```

## Modal Management

### Modal Display Controls
Shows and hides modals for different operations:

```javascript
document.querySelectorAll(".edit-btn").forEach(button => {
  button.addEventListener("click", function() {
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
```

### Modal Dismissal
Multiple ways to close modals for better usability:
- Close buttons in the modal header
- Cancel buttons
- Clicking outside the modal area

```javascript
window.addEventListener("click", function(event) {
  if (event.target === deleteModal) {
    deleteModal.style.display = "none";
    userIdToResetPassword = null;
  }
  if (event.target === editModal) {
    editModal.style.display = "none";
  }
  if (event.target === resetPasswordModal) {
    resetPasswordModal.style.display = "none";
    document.getElementById("tempPasswordContainer").style.display = "none";
  }
});
```

## Security Features

### CSRF Protection
All AJAX requests include CSRF tokens for security:

```javascript
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");

fetch("/admin/update_user", {
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken || "",
  },
  // ...
})
```

### Loading States
Disables buttons during operations to prevent duplicate submissions:

```javascript
// Show loading state
const resetBtn = this;
const originalText = resetBtn.textContent;
resetBtn.textContent = "Resetting...";
resetBtn.disabled = true;

// ... after operation completes or fails ...

// Reset button state
resetBtn.textContent = originalText;
resetBtn.disabled = false;
```

## Error Handling

### Comprehensive Error Processing
Multiple layers of error handling for robust operation:

```javascript
.then(response => {
  if (!response.ok) {
    return response.json().then(data => {
      throw new Error(data.message || "Server error occurred");
    });
  }
  return response.json();
})
.catch(error => {
  console.error("Error details:", error);
  showToast(`Failed to reset password: ${error.message || "Unknown error"}`, true);
});
```

## Initialization
The entire script is wrapped in a DOMContentLoaded event listener to ensure the DOM is fully loaded before attaching event handlers:

```javascript
document.addEventListener("DOMContentLoaded", function() {
  // All initialization code here
});
```