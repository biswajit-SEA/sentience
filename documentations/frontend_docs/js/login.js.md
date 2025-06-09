# `login.js` Documentation

## Overview
This JavaScript file handles the login form validation and user interaction for the Customer Churn Prediction System. It ensures that user credentials are properly validated before submission and enhances the user experience with features like password visibility toggling.

## Key Features
- Client-side form validation
- Email format verification
- Empty password detection
- reCAPTCHA validation
- Password visibility toggle

## Form Validation

### Form Submission Handler
The script attaches an event listener to the login form that validates all inputs before allowing submission:

```javascript
document.getElementById("loginForm").addEventListener("submit", function(event) {
  let isValid = true;
  
  // Validation code...
  
  if (!isValid) {
    event.preventDefault();
  }
});
```

### Email Validation
Checks that the email address follows a standard format:

```javascript
const emailInput = document.getElementById("email");
const emailError = document.getElementById("emailError");
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

if (!emailPattern.test(emailInput.value)) {
  emailError.textContent = "Please enter a valid email address";
  emailInput.style.borderColor = "red";
  isValid = false;
} else {
  emailError.textContent = "";
  emailInput.style.borderColor = "";
}
```

### Password Validation
Ensures the password field is not empty:

```javascript
const passwordInput = document.getElementById("password");
const passwordError = document.getElementById("passwordError");

if (passwordInput.value.trim() === "") {
  passwordError.textContent = "Password cannot be empty";
  passwordInput.style.borderColor = "red";
  isValid = false;
} else {
  passwordError.textContent = "";
  passwordInput.style.borderColor = "";
}
```

### reCAPTCHA Validation
Verifies that the reCAPTCHA challenge has been completed:

```javascript
const recaptchaResponse = grecaptcha.getResponse();
const recaptchaError = document.getElementById("recaptchaError");

if (recaptchaResponse.length === 0) {
  recaptchaError.style.display = "block";
  isValid = false;
} else {
  recaptchaError.style.display = "none";
}
```

## User Experience Enhancements

### Password Visibility Toggle
Allows users to show or hide the password text to ensure accurate entry:

```javascript
const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

togglePassword.addEventListener("click", function() {
  const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
  passwordInput.setAttribute("type", type);
  this.innerHTML = type === "password" 
    ? '<i class="fas fa-eye"></i>' 
    : '<i class="fas fa-eye-slash"></i>';
});
```

## Visual Feedback
The validation process provides visual cues to help users understand and correct issues:

- Red border around invalid fields
- Error messages explaining validation failures
- Icon toggle for password visibility state