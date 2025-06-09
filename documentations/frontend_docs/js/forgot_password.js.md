# `forgot_password.js` Documentation

## Overview
This JavaScript file handles the form validation for the password recovery process in the Customer Churn Prediction System. It ensures that user input is properly validated before the password reset request is submitted.

## Key Features
- Email format validation
- reCAPTCHA validation
- Visual feedback for validation errors
- Loading spinner during form submission

## Form Validation

### Form Submission Handler
The script attaches an event listener to the password recovery form that validates all inputs before allowing submission:

```javascript
document.getElementById("forgotPasswordForm").addEventListener("submit", function(event) {
  let isValid = true;
  
  // Validation code...
  
  if (!isValid) {
    event.preventDefault();
  } else {
    // Showing loading spinner when the form is submitted and validation passes
    document.getElementById("spinnerOverlay").style.display = "flex";
  }
});
```

### Email Validation
Verifies that the provided email address follows standard format:

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

### reCAPTCHA Validation
Ensures the reCAPTCHA challenge is completed to prevent automated form submissions:

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

## Visual Feedback

### Error Messages
The validation process displays clear error messages when input is invalid:
- Error text appearing below input fields
- Red border highlighting for invalid fields
- Visible error message for incomplete reCAPTCHA

### Loading Indication
A loading spinner appears during form submission to indicate processing:

```javascript
document.getElementById("spinnerOverlay").style.display = "flex";
```

## Security Features
- Email format validation prevents malformed addresses
- reCAPTCHA integration prevents bot submissions
- Client-side validation improves user experience while server-side validation ensures security