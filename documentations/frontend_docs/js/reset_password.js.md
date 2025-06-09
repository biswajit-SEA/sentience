# `reset_password.js` Documentation

## Overview
This JavaScript file implements the password reset functionality for the Customer Churn Prediction System. It provides real-time password validation, strength measurement, and form validation to ensure users create strong, secure new passwords after requesting a password reset.

## Key Features
- Real-time password strength evaluation
- Visual password requirement indicators
- Password visibility toggles
- Common password detection
- Password confirmation matching
- Form validation on submission

## Password Requirements System

### Requirement Visual Indicators
The script implements visual indicators for five password requirements:
```javascript
const lengthReq = document.getElementById("length-requirement");
const uppercaseReq = document.getElementById("uppercase-requirement");
const lowercaseReq = document.getElementById("lowercase-requirement");
const numberReq = document.getElementById("number-requirement");
const specialReq = document.getElementById("special-requirement");
```

Each requirement updates in real-time as the user types:
- Green checkmark (✓) when fulfilled
- Red X mark (✕) when not fulfilled

### Strength Measurement
Password strength is calculated by counting fulfilled requirements:

```javascript
let strength = 0;
if (password.length >= 8) strength++;
if (/[A-Z]/.test(password)) strength++;
if (/[a-z]/.test(password)) strength++;
if (/[0-9]/.test(password)) strength++;
if (/[^A-Za-z0-9]/.test(password)) strength++;
```

The strength is visually represented with:
1. Text description ("Very Weak" to "Strong")
2. Color-coded text and progress bar
3. Progress bar that fills proportionally to strength

```javascript
strengthMeterFill.style.width = (strength * 20) + "%";

if (strength <= 2) {
  passwordStrength.textContent = "Very Weak";
  passwordStrength.className = "password-strength very-weak";
  strengthMeterFill.className = "strength-meter-fill very-weak";
} else if (strength === 3) {
  // ...and so on
}
```

## Common Password Detection

A list of frequently used passwords is checked against the user's input:

```javascript
const commonPasswords = [
  "123456", "password", "123456789", "12345678", "12345",
  "1234567", "qwerty", "abc123", "password1", "123123",
];

// Check if entered password is in the common passwords list
if (commonPasswords.includes(password)) {
  commonPasswordWarning.style.display = "block";
} else {
  commonPasswordWarning.style.display = "none";
}
```

## Password Visibility Toggles

Both password fields have visibility toggles to help users see what they've typed:

```javascript
togglePassword.addEventListener("click", function() {
  const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
  passwordInput.setAttribute("type", type);
  this.innerHTML = type === "password" 
    ? '<i class="fas fa-eye"></i>' 
    : '<i class="fas fa-eye-slash"></i>';
});

// Similar toggle for confirmation password
```

## Form Validation

### Password Confirmation Matching
Real-time validation of password confirmation matching:

```javascript
confirmPasswordInput.addEventListener("input", function() {
  if (this.value === passwordInput.value) {
    confirmPasswordError.textContent = "";
    confirmPasswordInput.style.borderColor = "";
  } else {
    confirmPasswordError.textContent = "Passwords do not match";
    confirmPasswordInput.style.borderColor = "red";
  }
});
```

### Form Submission Validation
Comprehensive validation before form submission:

```javascript
document.getElementById("resetPasswordForm").addEventListener("submit", function(event) {
  let isValid = true;
  
  // Password pattern compliance check
  const passwordPattern = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z\\d]).{8,}$");
  if (!passwordPattern.test(passwordInput.value)) {
    passwordError.textContent = "Password must meet all the requirements";
    passwordInput.style.borderColor = "red";
    isValid = false;
  }
  
  // Password confirmation match check
  if (confirmPasswordInput.value !== passwordInput.value) {
    confirmPasswordError.textContent = "Passwords do not match";
    confirmPasswordInput.style.borderColor = "red";
    isValid = false;
  }
  
  // Prevent form submission or show loading spinner
  if (!isValid) {
    event.preventDefault();
  } else {
    document.getElementById("spinnerOverlay").style.display = "flex";
  }
});
```

## Security Features

1. **Strong Password Requirements**:
   - Minimum 8 characters
   - At least 1 uppercase letter
   - At least 1 lowercase letter
   - At least 1 number
   - At least 1 special character

2. **Common Password Detection**: Warns against using frequently compromised passwords

3. **Password Validation Pattern**:
   ```javascript
   const passwordPattern = new RegExp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z\\d]).{8,}$");
   ```

## User Experience Enhancements

- **Real-time Validation**: Immediate feedback as the user types
- **Strength Visualization**: Color-coded strength meter
- **Requirement Checklist**: Visual indicators for each requirement
- **Password Visibility Toggles**: Help users see what they've typed
- **Loading Indicator**: Spinner during password reset submission