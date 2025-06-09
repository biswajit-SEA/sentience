# `change_password.js` Documentation

## Overview
This JavaScript file implements the password change functionality for the Customer Churn Prediction System. It provides real-time password strength validation, password requirement checking, and form validation to ensure secure password changes.

## Key Features
- Real-time password strength evaluation
- Visual password requirement indicators
- Password visibility toggle for all password fields
- Common password detection
- Current and new password difference validation
- Confirmation password matching

## Password Validation System

### Strength Indicators
```javascript
const passwordStrength = document.getElementById("passwordStrength");
const strengthMeterFill = document.getElementById("strengthMeterFill");
```

The script visualizes password strength with:
- Color-coded text indicator (very weak, weak, medium, strong)
- Progress bar that fills based on strength level
- Requirement checkboxes that update in real-time

### Password Requirements
The system checks for five password requirements:
1. Minimum length (8 characters)
2. Uppercase letters
3. Lowercase letters
4. Numbers
5. Special characters

```javascript
// Checking each requirement
// 1. Length check
if (password.length >= 8) {
  lengthReq.classList.add("fulfilled");
  lengthReq.classList.remove("unfulfilled");
  lengthReq.querySelector(".requirement-icon").textContent = "✓";
} else {
  lengthReq.classList.add("unfulfilled");
  lengthReq.classList.remove("fulfilled");
  lengthReq.querySelector(".requirement-icon").textContent = "✕";
}
```

### Strength Calculation
Password strength is calculated based on meeting the five requirements:

```javascript
// Password strength check
let strength = 0;
if (password.length >= 8) strength++;
if (/[A-Z]/.test(password)) strength++;
if (/[a-z]/.test(password)) strength++;
if (/[0-9]/.test(password)) strength++;
if (/[^A-Za-z0-9]/.test(password)) strength++;

if (strength <= 2) {
  passwordStrength.textContent = "Very Weak";
  passwordStrength.className = "password-strength very-weak";
  strengthMeterFill.className = "strength-meter-fill very-weak";
} else if (strength === 3) {
  passwordStrength.textContent = "Weak";
  // ...and so on
}
```

### Common Password Detection
Checks if the password is in a list of commonly used passwords:

```javascript
// Common password check
if (commonPasswords.includes(password)) {
  commonPasswordWarning.style.display = "block";
} else {
  commonPasswordWarning.style.display = "none";
}
```

## Password Visibility Toggles

The script implements visibility toggles for all three password fields:

### Current Password Toggle
```javascript
toggleCurrentPassword.addEventListener("click", function() {
  const type = currentPasswordInput.getAttribute("type") === "password" ? "text" : "password";
  currentPasswordInput.setAttribute("type", type);
  this.innerHTML = type === "password" 
    ? '<i class="fas fa-eye"></i>' 
    : '<i class="fas fa-eye-slash"></i>';
});
```

### New Password Toggle
```javascript
toggleNewPassword.addEventListener("click", function() {
  const type = newPasswordInput.getAttribute("type") === "password" ? "text" : "password";
  newPasswordInput.setAttribute("type", type);
  this.innerHTML = type === "password" 
    ? '<i class="fas fa-eye"></i>' 
    : '<i class="fas fa-eye-slash"></i>';
});
```

### Confirm Password Toggle
Similar toggle functionality for the confirm password field.

## Form Validation

### Real-time Password Matching
Validates that the confirmation password matches the new password:

```javascript
confirmPasswordInput.addEventListener("input", function() {
  if (this.value === newPasswordInput.value) {
    confirmPasswordError.textContent = "";
    confirmPasswordInput.style.borderColor = "";
  } else {
    confirmPasswordError.textContent = "Passwords do not match";
    confirmPasswordInput.style.borderColor = "red";
  }
});
```

### Form Submission Validation
Comprehensive validation on form submission:

```javascript
document.getElementById("changePasswordForm").addEventListener("submit", function(event) {
  let isValid = true;
  
  // Current password empty check
  // New password pattern check
  // Same password check
  // Confirm password match check
  
  if (!isValid) {
    event.preventDefault();
  } else {
    // Show loading spinner
    document.getElementById("spinnerOverlay").style.display = "flex";
  }
});
```

### Security Validations
1. **Current Password Check**: Ensures the current password is provided
2. **Reuse Prevention**: Prevents using the same password again
3. **Complexity Requirements**: Enforces password pattern compliance
4. **Confirmation Match**: Ensures both new password fields match

## Visual Feedback
The system provides visual feedback for users:
- Green checkmarks for fulfilled requirements
- Red X marks for unfulfilled requirements
- Color-coded strength meter
- Border highlighting for invalid fields
- Error messages for validation failures